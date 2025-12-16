import sys
import json
from itertools import permutations
from typing import Optional, List, Dict

from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsTextItem,
                               QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFileDialog, QMessageBox, QLabel, QPushButton)
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPathStroker, QAction

# ==========================================
# 0. BACKEND (Вставлен сюда для удобства)
# ==========================================
class Solver_ege1:
    def __init__(self, vertexes, adjacencies):
        self.vertexes = {c: {*w} for c, *w in vertexes.split()}
        self.adjacencies = adjacencies

    def solve(self):
        nodes = sorted(list(self.vertexes.keys())) # Сортируем для стабильности
        n = len(nodes)
        if n > 9:
            raise ValueError("Этот алгоритм поддерживает максимум 9 вершин (цифры 1-9).")

        indices = "".join(str(i + 1) for i in range(n))

        for x in permutations(nodes):
            t = self.adjacencies
            # Создаем копию для замены, чтобы не испортить исходную при наложении
            temp_t = t
            for a, b in zip(indices, x):
                temp_t = temp_t.replace(a, b)
            
            # Парсим результат замены
            try:
                candidate_dict = {c: {*w} for c, *w in temp_t.split()}
            except ValueError:
                continue

            if self.vertexes == candidate_dict:
                # Возвращаем найденное соответствие: номер -> буква
                return dict(zip(indices, x))
        return None


# ==========================================
# 1. Configuration
# ==========================================
class GraphConfig:
    NODE_DIAMETER = 30
    NODE_RADIUS = NODE_DIAMETER / 2
    EDGE_WIDTH = 2
    MIN_DISTANCE = 50

    COLOR_BG = QColor(40, 40, 40)
    COLOR_NODE = QColor(0, 150, 255)
    COLOR_NODE_ACTIVE = QColor(255, 0, 150)
    COLOR_EDGE = QColor(200, 200, 200)
    COLOR_TEXT = QColor(255, 255, 255)

    TABLE_BG = QColor(50, 50, 50)
    TABLE_TEXT = QColor(255, 255, 255)
    TABLE_DIAGONAL = QColor(80, 80, 80)
    NODE_DIAMETER = 30
    NODE_RADIUS = NODE_DIAMETER / 2
    EDGE_WIDTH = 2
    MIN_DISTANCE = 50

    COLOR_BG = QColor(40, 40, 40)
    COLOR_NODE = QColor(0, 150, 255)
    COLOR_NODE_ACTIVE = QColor(255, 0, 150)
    COLOR_EDGE = QColor(200, 200, 200)
    COLOR_TEXT = QColor(255, 255, 255)

    TABLE_BG = QColor(50, 50, 50)
    TABLE_TEXT = QColor(255, 255, 255)
    TABLE_DIAGONAL = QColor(80, 80, 80)
    
    # НОВОЕ: Цвет для букв в таблице после решения
    TABLE_SOLVED_HEADER = QColor(0, 255, 127) # Spring Green


# ==========================================
# 2. Graph Visual Entities
# ==========================================
class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_item, dest_item):
        super().__init__()
        self.source = source_item
        self.dest = dest_item
        self.setPen(QPen(GraphConfig.COLOR_EDGE, GraphConfig.EDGE_WIDTH))
        self.setZValue(0)
        self.update_geometry()

    def update_geometry(self):
        line = QLineF(self.source.scenePos(), self.dest.scenePos())
        self.setLine(line)

    def shape(self):
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name: str, x: float, y: float):
        rect = QRectF(-GraphConfig.NODE_RADIUS, -GraphConfig.NODE_RADIUS,
                      GraphConfig.NODE_DIAMETER, GraphConfig.NODE_DIAMETER)
        super().__init__(rect)
        self.name = name
        self.edges: List[EdgeItem] = []
        self.setBrush(QBrush(GraphConfig.COLOR_NODE))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self._create_label(name)

    def _create_label(self, text: str):
        self.label = QGraphicsTextItem(text, self)
        self.label.setDefaultTextColor(GraphConfig.COLOR_TEXT)
        font = self.label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.label.setFont(font)
        # Центрируем текст
        br = self.label.boundingRect()
        self.label.setPos(-br.width() / 2, -br.height() / 2)
        
    def set_highlighted(self, is_active: bool):
        color = GraphConfig.COLOR_NODE_ACTIVE if is_active else GraphConfig.COLOR_NODE
        self.setBrush(QBrush(color))

    def add_connection(self, edge: EdgeItem):
        self.edges.append(edge)

    def remove_connection(self, edge: EdgeItem):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for edge in self.edges:
                edge.update_geometry()
        return super().itemChange(change, value)


# ==========================================
# 3. Graph Logic Managers
# ==========================================
class ChainBuilder:
    def __init__(self):
        self.active_node: Optional[NodeItem] = None

    def start_or_continue(self, node: NodeItem) -> Optional[NodeItem]:
        prev_node = self.active_node
        if self.active_node:
            self.active_node.set_highlighted(False)
        self.active_node = node
        self.active_node.set_highlighted(True)
        return prev_node

    def reset(self):
        if self.active_node:
            self.active_node.set_highlighted(False)
            self.active_node = None


class GraphManager(QObject):
    node_count_changed = Signal(int)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene

    def reset(self):
        self.scene.clear()
        self.node_count_changed.emit(0)

    # --- ИСПРАВЛЕНО: Логика именования ---
    def generate_name(self) -> str:
        """Находит первое свободное имя (A, B, C...), переиспользуя удаленные."""
        existing_names = set()
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                existing_names.add(item.name)
        
        i = 0
        while True:
            # Генерация имени: A, B ... Z, AA, AB ...
            name = ""
            temp_i = i
            while temp_i >= 0:
                name = chr(ord('A') + (temp_i % 26)) + name
                temp_i = temp_i // 26 - 1
            
            if name not in existing_names:
                return name
            i += 1

    def create_node(self, pos: QPointF, name: str = None) -> NodeItem:
        if name is None:
            name = self.generate_name()
        
        node = NodeItem(name, pos.x(), pos.y())
        self.scene.addItem(node)
        self.node_count_changed.emit(self.get_node_count())
        return node

    def create_edge(self, u: NodeItem, v: NodeItem):
        if u == v: return
        # Проверка дубликатов
        for edge in u.edges:
            if (edge.source == u and edge.dest == v) or (edge.source == v and edge.dest == u):
                return
        edge = EdgeItem(u, v)
        self.scene.addItem(edge)
        u.add_connection(edge)
        v.add_connection(edge)

    def delete_item(self, item: QGraphicsItem):
        if isinstance(item, NodeItem):
            for edge in list(item.edges):
                self.delete_item(edge)
            self.scene.removeItem(item)
            self.node_count_changed.emit(self.get_node_count())
        elif isinstance(item, EdgeItem):
            item.source.remove_connection(item)
            item.dest.remove_connection(item)
            self.scene.removeItem(item)
        elif isinstance(item, QGraphicsTextItem):
            parent = item.parentItem()
            if isinstance(parent, NodeItem):
                self.delete_item(parent)

    def get_node_count(self) -> int:
        return sum(1 for item in self.scene.items() if isinstance(item, NodeItem))

    def is_position_valid(self, pos: QPointF) -> bool:
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                distance = QLineF(pos, item.scenePos()).length()
                if distance < GraphConfig.MIN_DISTANCE:
                    return False
        return True


# ==========================================
# 4. Matrix Widget
# ==========================================
class WeightMatrixWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(0)
        self.setRowCount(0)
        # Немного обновим стили для заголовков
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {GraphConfig.TABLE_BG.name()};
                color: {GraphConfig.TABLE_TEXT.name()};
                gridline-color: #666;
            }}
            QHeaderView::section {{
                background-color: #333;
                color: white;
                padding: 4px;
                border: 1px solid #666;
                font-weight: bold; 
            }}
            QLineEdit {{ color: white; background-color: #444; }}
        """)
        self.itemChanged.connect(self.on_item_changed)
        self.horizontalHeader().setDefaultSectionSize(40)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Храним текущее состояние (цифры или буквы)
        self.is_solved_view = False

    def update_size(self, node_count: int):
        # При изменении размера всегда сбрасываем вид к цифрам
        self.is_solved_view = False
        
        self.setRowCount(node_count)
        self.setColumnCount(node_count)

        self.reset_labels() # Устанавливаем цифры 1, 2, 3...

        self.blockSignals(True)
        for r in range(node_count):
            for c in range(node_count):
                item = self.item(r, c)
                if not item:
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(r, c, item)

                if r == c:
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setBackground(QBrush(GraphConfig.TABLE_DIAGONAL))
                else:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                    item.setBackground(QBrush(GraphConfig.TABLE_BG))
        self.blockSignals(False)

    def on_item_changed(self, item):
        row, col = item.row(), item.column()
        if row == col: return
        
        text = item.text()
        if text and not text.isdigit():
             item.setText("")
             return

        self.blockSignals(True)
        symmetric_item = self.item(col, row)
        if symmetric_item:
            symmetric_item.setText(text)
        self.blockSignals(False)

    def get_data(self) -> List[List[str]]:
        rows = self.rowCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(rows):
                item = self.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def set_data(self, data: List[List[str]]):
        size = len(data)
        self.update_size(size)
        self.blockSignals(True)
        for r in range(size):
            for c in range(size):
                if r < len(data) and c < len(data[r]):
                    val = data[r][c]
                    item = self.item(r, c)
                    if item:
                        item.setText(val)
        self.blockSignals(False)

    # --- НОВЫЕ МЕТОДЫ ---
    
    def apply_labels(self, mapping: dict):
        """Заменяет цифры заголовков на буквы из словаря mapping"""
        self.is_solved_view = True
        rows = self.rowCount()
        
        for i in range(rows):
            key = str(i + 1) # Ключи в mapping это строки '1', '2'...
            label_text = mapping.get(key, "?") # Получаем букву
            
            # Создаем красивый заголовок
            item_h = QTableWidgetItem(label_text)
            item_h.setForeground(QBrush(GraphConfig.TABLE_SOLVED_HEADER))
            # Можно увеличить шрифт для наглядности
            font = item_h.font()
            font.setPointSize(12)
            font.setBold(True)
            item_h.setFont(font)
            
            self.setHorizontalHeaderItem(i, item_h)
            
            # То же самое для вертикального заголовка
            item_v = QTableWidgetItem(label_text)
            item_v.setForeground(QBrush(GraphConfig.TABLE_SOLVED_HEADER))
            item_v.setFont(font)
            self.setVerticalHeaderItem(i, item_v)

    def reset_labels(self):
        """Возвращает цифры 1, 2, 3..."""
        self.is_solved_view = False
        rows = self.rowCount()
        headers = [str(i + 1) for i in range(rows)]
        
        # setLabels сбрасывает кастомное форматирование (цвета)
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

# ==========================================
# 5. Graph Scene & View (ИСПРАВЛЕННЫЙ)
# ==========================================
class GraphScene(QGraphicsScene):
    def __init__(self, manager: GraphManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.chain_builder = ChainBuilder()
        self.setBackgroundBrush(QBrush(GraphConfig.COLOR_BG))
        self.setSceneRect(0, 0, 800, 600)

    def keyReleaseEvent(self, event):
        # Если отпустили Shift, сбрасываем выделение первого узла
        if event.key() == Qt.Key_Shift:
            self.chain_builder.reset()
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        # Получаем предмет под курсором
        # Обратите внимание: views()[0] может быть небезопасно, если view еще нет,
        # но в рамках события мыши view точно существует.
        transform = self.views()[0].transform() if self.views() else None
        item = self.itemAt(pos, transform) if transform else None

        # --- ИСПРАВЛЕНИЕ ТУТ ---
        # Если кликнули в Текст, берем его родителя (Узел)
        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()
        # -----------------------

        if event.button() == Qt.LeftButton:
            # Логика создания ребра (Shift + Click)
            if event.modifiers() & Qt.ShiftModifier:
                if isinstance(item, NodeItem):
                    # Пытаемся продолжить цепочку
                    prev_node = self.chain_builder.start_or_continue(item)
                    if prev_node:
                        # Если это второй узел в цепочке - создаем ребро
                        self.manager.create_edge(prev_node, item)
                        # Сбрасываем выбор после создания ребра, 
                        # чтобы можно было начать новое соединение сразу
                        self.chain_builder.reset() 
                    event.accept()
                    return
                else:
                    # Кликнули в пустоту с Шифтом - сброс
                    self.chain_builder.reset()
            else:
                # Кликнули без Шифта - сброс выделения
                self.chain_builder.reset()

            # Логика создания узла (если кликнули в пустоту)
            if item is None:
                if self.manager.is_position_valid(pos):
                    self.manager.create_node(pos)
                event.accept()
                return

            super().mousePressEvent(event)

        elif event.button() == Qt.RightButton:
            self.chain_builder.reset()
            if item:
                self.manager.delete_item(item)
                event.accept()


# ==========================================
# 6. Main Application Window
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тренажер: Граф и Матрица весов")
        self.resize(1200, 700)

        self.scene = QGraphicsScene()
        self.graph_manager = GraphManager(self.scene)
        self.scene = GraphScene(self.graph_manager, self)
        self.graph_manager.scene = self.scene

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.matrix_widget = WeightMatrixWidget()

        self.graph_manager.node_count_changed.connect(self.matrix_widget.update_size)

        # Layouts
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Left Panel (Matrix)
        left_layout = QVBoxLayout()
        left_label = QLabel("Матрица весов")
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.matrix_widget)
        
        # --- КНОПКИ УПРАВЛЕНИЯ ---
        buttons_layout = QHBoxLayout()
        
        self.btn_solve = QPushButton("Найти соответствие (Решить)")
        self.btn_solve.setFixedHeight(40)
        self.btn_solve.setStyleSheet("background-color: #2a82da; color: white; font-weight: bold;")
        self.btn_solve.clicked.connect(self.run_solver)
        
        self.btn_reset_view = QPushButton("Сбросить буквы")
        self.btn_reset_view.setFixedHeight(40)
        self.btn_reset_view.setStyleSheet("background-color: #555; color: white;")
        self.btn_reset_view.clicked.connect(self.reset_matrix_view)
        
        buttons_layout.addWidget(self.btn_solve, 2)
        buttons_layout.addWidget(self.btn_reset_view, 1)
        
        left_layout.addLayout(buttons_layout)

        # Right Panel (Graph)
        right_layout = QVBoxLayout()
        right_label = QLabel("Редактор графа (ЛКМ - узел, Shift+ЛКМ - ребро, ПКМ - удалить)")
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.view)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)

        self.setCentralWidget(central_widget)
        self.create_menu()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")

        save_action = QAction("Сохранить упражнение...", self)
        save_action.triggered.connect(self.save_exercise)
        file_menu.addAction(save_action)

        load_action = QAction("Загрузить упражнение...", self)
        load_action.triggered.connect(self.load_exercise)
        file_menu.addAction(load_action)

        clear_action = QAction("Очистить всё", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

    def clear_all(self):
        self.graph_manager.reset()
        self.matrix_widget.update_size(0)

    # --- ИНТЕГРАЦИЯ БЭКЕНДА ---
    def get_graph_string(self) -> str:
        """Собирает строку вида 'ABDG BAGC ...' из нарисованного графа"""
        result_parts = []
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        
        # Сортируем узлы по имени (A, B, C...)
        nodes.sort(key=lambda n: n.name)

        for node in nodes:
            # Находим соседей
            neighbors = []
            for edge in node.edges:
                other = edge.dest if edge.source == node else edge.source
                neighbors.append(other.name)
            
            # Формат: 'A' + 'BCD' (сортированные соседи)
            part = node.name + "".join(sorted(neighbors))
            result_parts.append(part)
            
        return " ".join(result_parts)

    def get_matrix_string(self) -> str:
        """Собирает строку вида '126 2147 ...' из таблицы"""
        rows = self.matrix_widget.rowCount()
        result_parts = []
        
        for r in range(rows):
            # Номер текущей строки (вершины) в 1-based формате
            row_idx = r + 1
            neighbors_indices = []
            
            for c in range(rows):
                if r == c: continue
                item = self.matrix_widget.item(r, c)
                # Если в ячейке есть число (вес), значит есть связь
                if item and item.text().strip():
                    neighbors_indices.append(str(c + 1))
            
            if neighbors_indices:
                part = str(row_idx) + "".join(sorted(neighbors_indices))
                result_parts.append(part)
            else:
                # Если вершина изолирована в таблице, бэкенд может это не переварить, 
                # но добавим просто номер строки
                result_parts.append(str(row_idx))
                
        return " ".join(result_parts)

    # Новая функция для кнопки сброса
    def reset_matrix_view(self):
        self.matrix_widget.reset_labels()

    def run_solver(self):
        # Если уже решено - сначала сбрасываем для чистоты
        self.reset_matrix_view()
        
        graph_str = self.get_graph_string()
        matrix_str = self.get_matrix_string()

        # Debug print
        print(f"Graph Input: {graph_str}")
        print(f"Matrix Input: {matrix_str}")

        if not graph_str or not matrix_str:
            QMessageBox.warning(self, "Ошибка", "Граф или таблица пусты.")
            return

        solver = Solver_ege1(graph_str, matrix_str)
        try:
            result = solver.solve()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при расчете: {e}")
            return

        if result:
            # result = {'1': 'C', '2': 'A', ...}
            
            # 1. Применяем буквы к таблице
            self.matrix_widget.apply_labels(result)
            
            # 2. Формируем сообщение
            msg = "Найдено соответствие! Таблица обновлена.\n\n"
            sorted_res = sorted(result.items(), key=lambda x: int(x[0]))
            for num, letter in sorted_res:
                msg += f"Пункт {num} -> {letter}\n"
            
            QMessageBox.information(self, "Успех", msg)
        else:
            QMessageBox.warning(self, "Неудача", "Соответствие не найдено.\nПроверьте, совпадают ли связи в графе и таблице.")
    # --- SAVE/LOAD (без изменений) ---
    def save_exercise(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "JSON Files (*.json)")
        if not file_path: return

        nodes_data = []
        node_id_map = {} 
        items = [i for i in self.scene.items() if isinstance(i, NodeItem)]
        
        for idx, node in enumerate(items):
            node_id_map[node] = idx
            nodes_data.append({
                "id": idx,
                "name": node.name,
                "x": node.pos().x(),
                "y": node.pos().y()
            })

        edges_data = []
        visited_edges = set()
        for node in items:
            for edge in node.edges:
                if edge not in visited_edges:
                    visited_edges.add(edge)
                    u_id = node_id_map.get(edge.source)
                    v_id = node_id_map.get(edge.dest)
                    if u_id is not None and v_id is not None:
                        edges_data.append({"u": u_id, "v": v_id})

        matrix_data = self.matrix_widget.get_data()
        data = { "graph": { "nodes": nodes_data, "edges": edges_data }, "matrix": matrix_data }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Успех", "Упражнение сохранено!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def load_exercise(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "JSON Files (*.json)")
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.clear_all()
            graph_data = data.get("graph", {})
            nodes_list = graph_data.get("nodes", [])
            edges_list = graph_data.get("edges", [])

            # Восстанавливаем узлы
            id_to_node = {}
            for n_data in nodes_list:
                pos = QPointF(n_data["x"], n_data["y"])
                name = n_data["name"]
                node = self.graph_manager.create_node(pos, name)
                id_to_node[n_data["id"]] = node

            # Восстанавливаем ребра
            for e_data in edges_list:
                u = id_to_node.get(e_data["u"])
                v = id_to_node.get(e_data["v"])
                if u and v:
                    self.graph_manager.create_edge(u, v)

            self.matrix_widget.set_data(data.get("matrix", []))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark Theme Palette
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.WindowText, Qt.white)
    palette.setColor(palette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ToolTipBase, Qt.white)
    palette.setColor(palette.ColorRole.ToolTipText, Qt.white)
    palette.setColor(palette.ColorRole.Text, Qt.white)
    palette.setColor(palette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ButtonText, Qt.white)
    palette.setColor(palette.ColorRole.BrightText, Qt.red)
    palette.setColor(palette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())