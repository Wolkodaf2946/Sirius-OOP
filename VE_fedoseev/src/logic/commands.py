from PySide6.QtGui import QUndoCommand

class AddShapeCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        
        name = "Shape"
        if hasattr(item, "type_name"):
            name = item.type_name
        self.setText(f"Add {name}")
    
    def redo(self):
        if self.item.scene() != self.scene:
            self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class ChangeColorCommand(QUndoCommand):
    def __init__(self, item, color):
        super().__init__()
        self.item = item
        self.new_color = color

        self.old_color = item.pen().color().name()

        self.setText(f"Changed color to {color}")

    def redo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.new_color)
    
    def undo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.old_color)

class MoveCommand(QUndoCommand):
    def __init__(self, item, start_pos, end_pos):
        super().__init__()
        self.item = item
        self.start = start_pos
        self.end = end_pos
        self.setText(f"Move {item.type_name}")

    def redo(self):
        self.item.setPos(self.end)

    def undo(self):
        self.item.setPos(self.start)


class DeleteCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.setText(f"Delete {item.type_name}")
    
    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)

class ChangeColorCommand(QUndoCommand):
    def __init__(self, item, new_color):
        super().__init__()
        self.item = item
        self.new_color = new_color

        if hasattr(item, "pen"):
            self.old_color = item.pen().color().name()
        else:
            self.old_color = "000000"

        self.setText(f"Change Color to {new_color}")

    def redo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.new_color)

    def undo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.old_color)

class ChangeWidthCommand(QUndoCommand):
    def __init__(self, item, new_width):
        super().__init__()
        self.item = item
        self.new_width = new_width

        if hasattr(item, "pen"):
            self.old_width = item.pen().width()
        else:
            self.old_width = 1

        self.setText(f"Change Width to {new_width}")
        
    def redo(self):
        if hasattr(self.item, "set_stroke_width"):
            self.item.set_stroke_width(self.new_width)

    def undo(self):
        if hasattr(self.item, "set_stroke_width"):
            self.item.set_stroke_width(self.old_width)