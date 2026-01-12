from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QFrame, QColorDialog, QHBoxLayout, QDoubleSpinBox
from PySide6.QtCore import Qt
from src.logic.commands import ChangeColorCommand, ChangeWidthCommand
from shiboken6 import isValid

class PropertiesPanel(QWidget):
    def __init__(self, scene, undo_stack):
        super().__init__()
        self.scene = scene
        self.undo_stack = undo_stack

        self._init_ui()

        # Подключаемся к сигналу изменения выделения сцены
        self.scene.selectionChanged.connect(self.on_selection_changed)


    def _init_ui(self):
        self.setFixedWidth(200)
        #self.setStyleSheet("background-color: #000000; border-left: 1px solid #ccc;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Свойства")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        self.lbl_type = QLabel("Тип не выбран")
        self.lbl_type.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_type)

        layout.addWidget(QLabel("Толщина обводки:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1,50)
        layout.addWidget(self.spin_width)

        layout.addWidget(QLabel("Цвет линии:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(30)

        layout.addWidget(self.btn_color)

        self.setEnabled(False)
        self.spin_width.valueChanged.connect(self.on_width_changed)
        self.btn_color.clicked.connect(self.on_color_clicked)

        geo_layout = QHBoxLayout()

        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setPrefix("X: ")
        self.spin_x.valueChanged.connect(self.on_geo_changed)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.valueChanged.connect(self.on_geo_changed)

        geo_layout.addWidget(self.spin_x)
        geo_layout.addWidget(self.spin_y)
        layout.addLayout(geo_layout)
        layout.addStretch()

    def _is_scene_valid(self):
        #Проверяет, что сцена существует и валидна
        return self.scene is not None and isValid(self.scene)

    def on_selection_changed(self):
        if not self._is_scene_valid():
            return
        selected_items = self.scene.selectedItems()

        if not selected_items:
            self.setEnabled(False)
            self.spin_width.setValue(1)
            self.btn_color.setStyleSheet("background-color: transparent")

            self.spin_width.setToolTip("")

            self.lbl_type.setText("Тип не выбран")

            self.spin_x.blockSignals(True)
            self.spin_y.blockSignals(True)
            self.spin_x.setValue(0)
            self.spin_y.setValue(0)
            self.spin_x.blockSignals(False)
            self.spin_y.blockSignals(False)

            return
        
        self.setEnabled(True)

        self.update_width_ui(selected_items)

        item = selected_items[0]

        current_width = 1
        current_color = "#f0f0f0"

        if hasattr(item, "pen") and item.pen() is not None:
            current_width = item.pen().width()
            current_color = item.pen().color().name()

        self.spin_width.blockSignals(True)
        self.spin_width.setValue(current_width)
        self.spin_width.blockSignals(False)

        self.btn_color.setStyleSheet(f"background-color: {current_color}; border: 1px solid gray;")

        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)
        
        self.spin_x.setValue(float(item.pos().x()))
        self.spin_y.setValue(float(item.pos().y()))

        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)

        if hasattr(item, "type_name"):
            type_text = item.type_name.capitalize()
        else:
            type_text = type(item).__name__

        if len(selected_items) > 1:
            type_text += f" (+{len(selected_items)-1})"

        self.lbl_type.setText(type_text)

    def on_width_changed(self, value):
        if not self._is_scene_valid():
            return
        selected_items = self.scene.selectedItems()

        if not selected_items:
            return

        self.undo_stack.beginMacro("Change Width All")

        for item in selected_items:
            cmd = ChangeWidthCommand(item, value)
            self.undo_stack.push(cmd)
        self.undo_stack.endMacro()
        self.scene.update()

    def on_color_clicked(self):
        if not self._is_scene_valid():
            return
        color = QColorDialog.getColor(title="Выберите цвет линии")

        if color.isValid():
            hex_color = color.name()
            current_width = self.spin_width.value()

            self.btn_color.setStyleSheet(f"background-color: {hex_color}; border: 1px solid gray;")
            selected_items = self.scene.selectedItems()

            if not selected_items:
                return
            
            self.undo_stack.beginMacro("Change Color All")

            for item in selected_items:
                cmd = ChangeColorCommand(item, hex_color)
                self.undo_stack.push(cmd)
                
            self.undo_stack.endMacro()

    def on_geo_changed(self):
        if not self._is_scene_valid():
            return
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            new_x = self.spin_x.value()
            new_y = self.spin_y.value()
            item.setPos(new_x, new_y)

        self.scene.update()

    def update_width_ui(self, selected_items):
        if not self._is_scene_valid():
            return
        self.spin_width.blockSignals(True)

        first_width = -1
        is_mixed = False

        for i, item in enumerate(selected_items):
            if not hasattr(item, "pen"): continue

            w = item.pen().width()

            if i == 0:
                first_width = w
            else:
                if w != first_width:
                    is_mixed = True
                    break

        if is_mixed:
            self.spin_width.setValue(first_width)
            self.spin_width.setStyleSheet("background-color: #fffacd;")
            self.spin_width.setToolTip("Выбраны объекты с разной толщиной")
        else:
            self.spin_width.setValue(first_width)
            self.spin_width.setStyleSheet("")
            self.spin_width.setToolTip("")
        
        self.spin_width.blockSignals(False)