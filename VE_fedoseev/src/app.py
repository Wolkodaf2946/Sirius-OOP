from PySide6.QtGui import QCloseEvent,QAction,QColor,QKeySequence
from PySide6.QtWidgets import QMainWindow,QMessageBox,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QFrame, QGridLayout, QSlider, QLabel, QColorDialog, QFileDialog
from src.widgets.canvas import EditorCanvas
from src.widgets.properties import PropertiesPanel
from src.logic.strategies import JsonSaveStrategy, ImageSaveStrategy
from PySide6.QtCore import Qt
from src.logic.io_manager import FileManager
import json

class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Vector Editor")
        self.resize(800, 600)

        self.current_tool = "line"
        self.current_color = "red"
        
        self._init_ui()

    def _init_ui(self):
        self._setup_layout()
        self.statusBar().showMessage("Готов к работе")

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Saving Project")
        save_action.triggered.connect(self.on_save_clicked)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        save_action.setStatusTip("Opening Project")
        open_action.triggered.connect(self.on_open_clicked)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close the application")
        exit_action.triggered.connect(self.close) 
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)
        
        # Тулбар
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(exit_action)

        #<+====================+>

        self.btn_line.clicked.connect(lambda: self.on_change_tool("line"))
        self.btn_rect.clicked.connect(lambda: self.on_change_tool("rect"))
        self.btn_ellipse.clicked.connect(lambda: self.on_change_tool("ellipse"))

        self.btn_color_picker.clicked.connect(self.on_color_select)
        self.btn_select.clicked.connect(lambda: self.on_change_tool("select"))

        group_action = QAction("Group", self)
        group_action.setShortcut(QKeySequence("Ctrl+G"))
        group_action.triggered.connect(self.canvas.group_selection)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.setShortcut(QKeySequence("Ctrl+U"))
        ungroup_action.triggered.connect(self.canvas.ungroup_selection)
        
        stack = self.canvas.undo_stack

        undo_action = stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.Undo)

        redo_action = stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.Redo)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.canvas.delete_selected)
        self.addAction(delete_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(group_action)
        edit_menu.addAction(ungroup_action)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(delete_action)

    def on_change_tool(self, tool_name: str):
        self.current_tool_str = tool_name
        self.statusBar().showMessage(f"Выбран инструмент: {tool_name}")
        
        if self.canvas:
            self.canvas.set_tool(tool_name)

    def _update_tool_buttons_ui(self, tool_name: str):
        self.btn_line.setChecked(False)
        self.btn_rect.setChecked(False)
        self.btn_ellipse.setChecked(False)
        self.btn_select.setChecked(False)

        if tool_name == "line":
            self.btn_line.setChecked(True)
        elif tool_name == "rect":
            self.btn_rect.setChecked(True)
        elif tool_name == "ellipse":
            self.btn_ellipse.setChecked(True)
        elif tool_name == "select":
            self.btn_select.setChecked(True)
        
        self.current_tool_str = tool_name

    def on_color_select(self):
        selected_color_qcolor = QColorDialog.getColor(
            QColor(self.current_color), self,
            "Choose a color for the shape"
        )
        
        if selected_color_qcolor.isValid():
            self.current_color = selected_color_qcolor.name()
            
            self.btn_color_picker.setStyleSheet(f"selected color: {self.current_color};")
            
            if self.canvas:
                self.canvas.set_current_color(self.current_color)

    def _setup_layout(self):
        container = QWidget()
        self.setCentralWidget(container)
        
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_line = QPushButton("Line")
        self.btn_rect = QPushButton("Rect")
        self.btn_ellipse = QPushButton("Ellipse")
        self.btn_color_picker = QPushButton("Select color")
        self.btn_select = QPushButton("Select")
        

        self.btn_line.setCheckable(True)
        self.btn_rect.setCheckable(True)
        self.btn_ellipse.setCheckable(True)
        self.btn_select.setCheckable(True)
        self.btn_line.setChecked(True)
        
        tools_panel = QFrame()
        tools_panel.setFixedWidth(120)
        tools_panel.setStyleSheet("background-color: #f0f0f0;") 
        
        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.addWidget(self.btn_line)
        tools_layout.addWidget(self.btn_rect)
        tools_layout.addWidget(self.btn_ellipse)
        tools_layout.addStretch()
        
        self.canvas = EditorCanvas()

        self.canvas.set_tool(self.current_tool)
        self.canvas.set_current_color(self.current_color)
        self.canvas.tool_changed.connect(self._update_tool_buttons_ui)

        self._update_tool_buttons_ui(self.current_tool)

        settings_panel = QFrame()
        settings_panel.setFixedWidth(240)
        settings_panel.setStyleSheet("background-color: #f0f0f0;")

        self.props_panel = PropertiesPanel(self.canvas.scene, self.canvas.undo_stack)

        settings_layout = QVBoxLayout(settings_panel)

        settings_layout.addWidget(self.btn_color_picker)

        settings_layout.addWidget(self.btn_select)

        settings_layout.addWidget(self.props_panel)
        settings_layout.addStretch()

        self.lbl_size = QLabel("Size: 2px")
        
        # 3. Слайдер
        self.slider_size = QSlider(Qt.Horizontal)
        self.slider_size.setRange(1, 100)
        self.slider_size.setValue(2)
        
        self.slider_size.valueChanged.connect(self.on_size_change)
        #settings_layout.addStretch()

        settings_layout.addWidget(self.lbl_size)
        settings_layout.addWidget(self.slider_size)

        main_layout.addWidget(tools_panel)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(settings_panel)

    def on_size_change(self, value):
        self.lbl_size.setText(f"Size: {value}px")
        
        if hasattr(self, 'canvas'):
            self.canvas.set_pen_size(value)

    def on_save_clicked(self):
        filters = "Vector Project (*.json);;PNG Image (*.png);;JPEG Image (*.jpg)"
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Save File", "", filters
        )

        if not filename:
            return
        
        strategy = None

        if filename.lower().endswith(".png"):
            strategy = ImageSaveStrategy("PNG", background="transparent")
        elif filename.lower().endswith(".jpg"):
            strategy = ImageSaveStrategy("JPG", background="white")
        else:
            strategy = JsonSaveStrategy()

        try:
            strategy.save(filename, self.canvas.scene)
            self.statusBar().showMessage(f"Успешно сохранено в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Не удалось сохранить файл:\n{str(e)}")

    def on_open_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект", "", "Vector Project (*.json *.vec)"
        )

        if not path:
            return
        
        data = FileManager.load_project(path)

        self.canvas.scene.clear()
        self.canvas.undo_stack.clear()

        scene_info = data.get("scene", {})
        width = scene_info.get("width", 800)
        height = scene_info.get("height", 600)
        self.canvas.scene.setSceneRect(0, 0, width, height)

        shapes_data = data.get("shapes", [])

        errors_count = 0

        for shape in shapes_data:
            try:
                shape_obj = ShapeFactory.from_dict(shape)
                self.canvas.scene.addItem(shape_obj)
            except Exception as e:
                print(f"Ошибка загрузки фигуры: {e}")
                errors_count += 1

        if errors_count > 0:
            self.statusBar().showMessage(f"Загружено с ошибками ({errors_count} фигур пропущено)")
        else:
            self.statusBar().showMessage(f"Проект загруже: {path}")

#---------------------------------------------------

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

