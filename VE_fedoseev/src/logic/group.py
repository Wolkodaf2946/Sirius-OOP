from PySide6.QtWidgets import QGraphicsItemGroup
from src.logic.shapes import Shape

class Group(QGraphicsItemGroup):
    def __init__(self):
        super().__init__()

        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable, True)

        self.setHandlesChildEvents(True)

    @property
    def type_name(self) -> str:
        return "group"
    
    def set_geometry(self, start_point, end_point):
        pass
    
    def set_active_color(self, color):
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_active_color(color)

    def to_dict(self):
        children = []
        for child in self.childItems():
            if isinstance(child, Shape):
                children.append(child.to_dict())

        return {
            "type": self.type_name,
            "x": self.pos.x(),
            "y": self.pos.y(),
            "children": children
        }
    
    