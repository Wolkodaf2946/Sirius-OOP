from abc import ABC, abstractmethod
from src.logic.factory import ShapeFactory
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QPointF, Qt
from src.logic.commands import *

class Tool(ABC):
    def __init__(self, canvas_view):
        self.view = canvas_view
        self.scene = canvas_view.scene

    @abstractmethod
    def mouse_press(self, event): pass

    @abstractmethod
    def mouse_move(self, event): pass

    @abstractmethod
    def mouse_release(self, event): pass

class CreationTool(Tool):
    MIN_DRAW_DISTANCE = 5

    def __init__(self, canvas_view, shape_type: str, undo_stack, color: str = None):
        super().__init__(canvas_view)
        self.shape_type = shape_type
        self.undo_stack = undo_stack
        self.color = color
        self.start_pos: QPointF = None
        self.current_shape: Shape = None

    def _get_color(self) -> str:
        if self.color:
            return self.color
        return getattr(self.view, 'current_color', 'black')

    def mouse_press(self, event):
        if event.button() != Qt.LeftButton:
            return
        
        self.start_pos = self.view.mapToScene(event.pos())
        self.current_shape = None

    def mouse_move(self, event):
        if not self.start_pos:
            return
        
        current_pos = self.view.mapToScene(event.pos())
        distance = (current_pos - self.start_pos).manhattanLength()

        if self.current_shape is None:
            if distance < self.MIN_DRAW_DISTANCE:
                return
            
            try:
                self.current_shape = ShapeFactory.create_shape(
                    self.shape_type,
                    self.start_pos,
                    self.start_pos,
                    self._get_color()
                )
                self.scene.addItem(self.current_shape)
            except ValueError as e:
                print(f"Ошибка создания фигуры: {e}")
                self.start_pos = None
                return

        if self.current_shape:
            self.current_shape.set_geometry(self.start_pos, current_pos)

    def mouse_release(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.current_shape:
            self.scene.removeItem(self.current_shape)
            
            end_pos = self.view.mapToScene(event.pos())
            try:
                final_shape = ShapeFactory.create_shape(
                    self.shape_type,
                    self.start_pos,
                    end_pos,
                    self._get_color()
                )
                
                command = AddShapeCommand(self.scene, final_shape)
                self.undo_stack.push(command)
                
                final_shape.setSelected(True)
                print(f"Фигура '{self.shape_type}' создана. Command: {command.text()}")
                
            except ValueError as e:
                print(f"Ошибка финализации фигуры: {e}")
        
        elif self.start_pos:
            print("Создание фигуры отменено (недостаточное движение мыши)")

        self.start_pos = None
        self.current_shape = None

class SelectionTool(Tool):
    def __init__(self, canvas_view, undo_stack):
        super().__init__(canvas_view)
        self.undo_stack = undo_stack
        self.item_positions = {}

    def mouse_press(self, event):
        QGraphicsView.mousePressEvent(self.view, event)
        
        if self.view.scene.itemAt(self.view.mapToScene(event.pos()), self.view.transform()):
            self.view.setCursor(Qt.ClosedHandCursor)

        self.item_positions.clear()
        for item in self.scene.selectedItems():
            self.item_positions[item] = item.pos()

    def mouse_move(self, event):
        QGraphicsView.mouseMoveEvent(self.view, event)
        
        item = self.view.itemAt(event.pos()) 
        
        if not (event.buttons() & Qt.LeftButton):
            if item:
                self.view.setCursor(Qt.OpenHandCursor)
            else:
                self.view.setCursor(Qt.ArrowCursor)

    def mouse_release(self, event):
        QGraphicsView.mouseReleaseEvent(self.view, event)
        self.view.setCursor(Qt.ArrowCursor)

        moved_items = []
        for item, start in self.item_positions.items():
            end = item.pos()
            if end != start:
                moved_items.append((item, start, end))

        if moved_items:
            self.undo_stack.beginMacro("Move Items")
            for item, start, end in moved_items:
                cmd = MoveCommand(item, start, end)
                self.undo_stack.push(cmd)
            self.undo_stack.endMacro()

        self.item_positions.clear()