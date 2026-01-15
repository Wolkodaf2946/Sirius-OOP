from PySide6.QtWidgets import (QMainWindow, QWidget,QVBoxLayout,QHBoxLayout,
QPushButton,QFrame,QMessageBox,QLabel,QLineEdit,QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QAction, QCloseEvent
from PySide6.QtCore import Qt, QRectF
from entity import Interval
from backend import Solver

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solver-EGE15")
        self.resize(950, 650)
        self._init_ui()

    def _init_ui(self):
        self._setup_layout()
        self.statusBar().showMessage("Solver-EGE15")

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close the application")
        exit_action.triggered.connect(self.close) 

        file_menu.addAction(exit_action)

    def _setup_layout(self):
        container = QWidget()
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)
        
        expression = QWidget()
        expression.setStyleSheet("background-color: #f0f0f0;") 
        
        expression_layout = QHBoxLayout(expression)
        expression_layout.setContentsMargins(0, 0, 0, 5)
        expression_layout.addWidget(QLabel("Выражение:"))
        self.formula_input = QLineEdit()
        self.formula_input.setText("") 
        expression_layout.addWidget(self.formula_input)
        #------------
        main_layout.addWidget(expression)

        help_label = QLabel("Синтаксис: (x in P), and, or, not, <= (импликация), == (равенство).")
        help_label.setStyleSheet("color: gray; font-size: 10px;") 
        #------------
        main_layout.addWidget(help_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Начало", "Конец"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(0)
        #------------
        main_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить отрезок")
        add_btn.clicked.connect(lambda: self.add_interval_row("Q", 0, 10))
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self.remove_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        #------------
        main_layout.addLayout(btn_layout)

        self.result_label = QLabel("Ожидание...")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        #------------
        main_layout.addWidget(self.result_label)

        self.interval_canvas = IntervalCanvas()
        #------------
        main_layout.addWidget(self.interval_canvas)

        settings_box = QWidget()
        settings_box.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")
        settings_layout = QHBoxLayout(settings_box)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Найти минимальный A", "Найти максимальный A"])
        settings_layout.addWidget(QLabel("Искать:"))
        settings_layout.addWidget(self.mode_combo)

        self.target_combo = QComboBox()
        self.target_combo.addItems(["Тождественно истинно (1)", "Тождественно ложно (0)"])
        settings_layout.addWidget(QLabel("Значение выражения:"))
        settings_layout.addWidget(self.target_combo)
        settings_layout.addStretch()
        
        calc_btn = QPushButton("Вычислить")
        calc_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border: none; padding: 5px 15px;")
        calc_btn.clicked.connect(self.run_calculation)
        settings_layout.addWidget(calc_btn)
        #------------
        main_layout.addWidget(settings_box)
        
    def add_interval_row(self, name, start, end):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(str(start)))
        self.table.setItem(row, 2, QTableWidgetItem(str(end)))
        self.table.setCurrentCell(row, 0) # новая строка будет активной
        self.table.setFocus() # сразу в новой строке можно писать

    def remove_row(self):
        row = self.table.currentRow() # индекс активной строки
        if row >= 0: self.table.removeRow(row)

    def get_intervals_from_ui(self):
        intervals = []
        try:
            for row in range(self.table.rowCount()):
                name = self.table.item(row, 0).text().strip()
                start = float(self.table.item(row, 1).text())
                end = float(self.table.item(row, 2).text())
                if name:
                    intervals.append(Interval(name, start, end))
            return intervals
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте числа в таблице")
            return None

    def run_calculation(self):
        intervals = self.get_intervals_from_ui()
        if not intervals: return

        formula = self.formula_input.text()
        mode = "min" if self.mode_combo.currentIndex() == 0 else "max"
        target_is_true = (self.target_combo.currentIndex() == 0)
        all_coords = [i.end for i in intervals]
        max_search = max(all_coords) + 30 if all_coords else 100
        
        solver = Solver(formula, intervals, search_range=(0, max_search))
        
        try:
            result_a = solver.solve(mode=mode, target_value=target_is_true)
            
            self.interval_canvas.update_data(intervals, result_a)
            
            target_text = "1" if target_is_true else "0"
            if result_a:
                self.result_label.setText(f"Чтобы выражение = {target_text}, {mode} отрезок A: [{result_a.start}, {result_a.end}]")
            else:
                self.result_label.setText(f"Для выражения = {target_text} решение не найдено (пустое множество)")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def closeEvent(self, event: QCloseEvent):
        print("Попытка закрыть окно...")
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            print("Window Closed: Разрешаем закрытие")
            event.accept()
        else:
            print("Отмена закрытия")
            event.ignore()

class IntervalCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(300)
        self.intervals = []
        self.result_interval = None

    def update_data(self, intervals, result):
        self.intervals = intervals
        self.result_interval = result
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # рисуем ось
        w = self.width()
        h = self.height()
        axis_x = 40
        axis_y = h - 50

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(axis_x, axis_y, w - axis_x, axis_y)

        # подбираем масштаб для правильного отображения координат
        all_vals = [0, 50]
        for i in self.intervals:
            all_vals.extend([i.start, i.end])
        if self.result_interval:
            all_vals.extend([self.result_interval.start, self.result_interval.end])
        
        min_val = min(all_vals)
        max_val = max(all_vals)
        scale_len = max_val - min_val
        if scale_len == 0: scale_len = 10

        # сколько пикселей экрана приходится на 1 единицу числа:
        px_per_unit = (w - 2 * axis_x) / scale_len

        def val_to_x(val):
            return axis_x + (val - min_val) * px_per_unit
        
        # отметки чисел на оси (засечки)
        step_grid = 10 if scale_len > 50 else 5
        if scale_len < 20: step_grid = 1
        
        current_grid = int(min_val)
        while current_grid <= int(max_val) + 1:
            x_pos = val_to_x(current_grid)
            if axis_x <= x_pos <= w - axis_x:
                painter.drawLine(int(x_pos), axis_y - 5, int(x_pos), axis_y + 5)
                painter.drawText(int(x_pos) - 10, axis_y + 20, str(current_grid))
            current_grid += step_grid

        # функция для отрисовки отрезка на оси
        def draw_interval_bar(interval, y_pos, color_code, is_result=False):
            x1 = val_to_x(interval.start)
            x2 = val_to_x(interval.end)
            
            if x2 < axis_x or x1 > w - axis_x: return
            x1 = max(x1, axis_x)
            x2 = min(x2, w - axis_x)
            
            width_bar = x2 - x1
            height_bar = 20
            rect = QRectF(x1, y_pos, width_bar, height_bar)
            
            color = QColor(color_code)
            color.setAlpha(150 if not is_result else 200) # прозрачность
            painter.setBrush(QBrush(color))
            
            pen = QPen(Qt.GlobalColor.black, 1)
            if is_result:
                pen = QPen(Qt.GlobalColor.red, 2)
            painter.setPen(pen)
            
            painter.drawRect(rect)
            label = f"{interval.name} [{interval.start}, {interval.end}]"
            painter.drawText(int(x1), int(y_pos) - 5, label)

        # отрисовка отрезков
        y_offset = axis_y - 40
        colors = [Qt.GlobalColor.blue, Qt.GlobalColor.green, Qt.GlobalColor.cyan, Qt.GlobalColor.magenta]
        
        for idx, interval in enumerate(self.intervals):
            c = colors[idx % len(colors)]
            draw_interval_bar(interval, y_offset, c)
            y_offset -= 35

        if self.result_interval:
            draw_interval_bar(self.result_interval, y_offset - 20, Qt.GlobalColor.red, is_result=True)
        else:
            painter.drawText(axis_x, 30, "Результат: нет подходящих точек")
