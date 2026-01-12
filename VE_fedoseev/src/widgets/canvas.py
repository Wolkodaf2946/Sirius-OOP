# Интеграция холста
from PySide6.QtGui import QPainter, QMouseEvent, QUndoStack
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PySide6.QtCore import Qt, QPoint, Signal
from src.logic.factory import ShapeFactory
from src.logic.shapes import Shape
from src.logic.group import Group
from src.logic.tools import CreationTool, SelectionTool, Tool
from src.logic.commands import DeleteCommand

class EditorCanvas(QGraphicsView):
    tool_changed = Signal(str)
    def __init__(self):
        super().__init__()
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 500, 500) 

        self.current_tool = "line"
        self.current_color = "red"
        self.current_size = 2

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(50)

        self.tools = {
            "select": SelectionTool(self, self.undo_stack),
            "line": CreationTool(self, "line", self.undo_stack),
            "rect": CreationTool(self, "rect", self.undo_stack),
            "ellipse": CreationTool(self, "ellipse", self.undo_stack),
        }
        self.active_tool: Tool = self.tools["line"]
        
        self.setRenderHint(self.renderHints() | QPainter.Antialiasing)
        self.setAlignment(Qt.AlignCenter)
        self.setMouseTracking(True)
        
        self._is_panning = False
        self._last_mouse_pos = QPoint()
        self.set_tool(self.current_tool)

    def set_tool(self, tool_name: str):
        if self.active_tool and isinstance(self.active_tool, CreationTool):
            if self.active_tool.current_shape:
                self.scene.removeItem(self.active_tool.current_shape)
                self.active_tool.current_shape = None
            self.active_tool.start_pos = None

        self.current_tool = tool_name
        self.active_tool = self.tools.get(tool_name, self.tools["select"])
        
        print(f"Canvas: active tool switched to {tool_name}")

        if tool_name == "select":
            self.setCursor(Qt.CursorShape.ArrowCursor) 
            for item in self.scene.items():
                if isinstance(item, Shape):
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        else: 
            self.setCursor(Qt.CursorShape.CrossCursor) 
            for item in self.scene.items():
                if isinstance(item, Shape):
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

        self.tool_changed.emit(tool_name)

    def set_current_color(self, color: str):
        self.current_color = color
        for item in self.scene.selectedItems():
            if isinstance(item, Shape):
                item.set_active_color(color)
        

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._start_panning(event)
            return

        if event.button() == Qt.LeftButton:
            item_at_pos = self.itemAt(event.pos())
            if isinstance(self.active_tool, CreationTool) and item_at_pos:
                self.set_tool("select") 
                self.active_tool.mouse_press(event)
                super().mousePressEvent(event)
                return 
            self.active_tool.mouse_press(event)
            return
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            if self.current_tool == "select":
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.setCursor(Qt.CursorShape.CrossCursor)
            event.accept()
            return

        self.active_tool.mouse_release(event)
        super().mouseReleaseEvent(event)

    def set_pen_size(self, size):
        self.current_size = size
        print(f"Canvas: толщина изменена на {size}")


    #------ Средняя кнопка мыши --------

    def _start_panning(self, event):
        self._is_panning = True
        self._last_mouse_pos = event.pos()
        self.setCursor(Qt.ClosedHandCursor)
        event.accept()


    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.pos() - self._last_mouse_pos
            self._last_mouse_pos = event.pos()
            
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        self.active_tool.mouse_move(event)
        super().mouseMoveEvent(event)


    def group_selection(self):
        try:
            print("Group Selection...")
            selected_items = self.scene.selectedItems()
            if not selected_items:
                return
            group = Group()
            self.scene.addItem(group)
            for item in selected_items:
                item.setSelected(False)
                group.addToGroup(item)
            group.setSelected(True)
            print("Group is created")
        except Exception as e:
            print (e)

    def ungroup_selection(self):
        selected_items = self.scene.selectedItems()

        for item in selected_items:
            if isinstance(item, Group):
                self.scene.destroyItemGroup(item)
                print("Group is ungrouped")

    def delete_selected(self):
        selected = self.scene.selectedItems()
        if not selected:
            return
        
        self.undo_stack.beginMacro("Delete Selected")

        for item in selected:
            cmd = DeleteCommand(self.scene, item)
            self.undo_stack.push(cmd)
        
        self.undo_stack.endMacro()
