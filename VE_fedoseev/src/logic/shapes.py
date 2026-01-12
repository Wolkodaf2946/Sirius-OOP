from abc import abstractmethod
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtCore import QPointF

# QGraphicsPathItem - дает графику
# ABC - делает класс абстрактным
class Shape(QGraphicsPathItem):
    def __init__(self, color: str = "black", stroke_width: int = 2):
        super().__init__()  # Обязательно инициализируем QGraphicsPathItem
        
        self.color = color
        self.stroke_width = stroke_width
        
        self._setup_pen()
        self._setup_flags()

    def _setup_pen(self):
        # Настройка внешнего вида (QPen - это "карандаш" для обводки)
        pen = QPen(QColor(self.color))
        pen.setWidth(self.stroke_width)
        self.setPen(pen)

    def _setup_flags(self):
        # Разрешаем выделение и перемещение

        # --- МАГИЯ QT ---
        # Включаем встроенные возможности интерактивности.
        # ItemIsSelectable: Фигура может быть выделена (вокруг появится рамка, если настроить)
        # ItemIsMovable: Фигуру можно таскать мышкой (Qt сам обработает drag-n-drop!)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
        # Разрешаем слать сигналы при изменении геометрии (пригодится позже)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
    def set_stroke_width(self, width: int):
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)

    def set_active_color(self, color: str):
        self.color = color
        self._setup_pen()

    # --- Абстрактный интерфейс ---
    @property
    @abstractmethod
    def type_name(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def set_geometry(self, start_point: QPointF, end_point: QPointF):
        pass
        


class Rectangle(Shape):
    def __init__(self, x,y,w,h,color="black",stroke_width=2):
        super().__init__(color, stroke_width)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        path.addRect(self.x, self.y, self.w, self.h)
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "rect"

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x, self.y],
            "props": {
                "x": self.x, "y": self.y,
                "w": self.w, "h": self.h,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }

    def set_geometry(self, start_point: QPointF, end_point: QPointF):
        self.x = min(start_point.x(), end_point.x())
        self.y = min(start_point.y(), end_point.y())
        self.w = abs(end_point.x() - start_point.x())
        self.h = abs(end_point.y() - start_point.y())
        self._create_geometry()

class Line(Shape):
    def __init__(self, x1, y1, x2, y2, color="black", stroke_width=2):
        super().__init__(color, stroke_width)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        # Инструкция: встань в начало
        path.moveTo(self.x1, self.y1)
        # Инструкция: проведи черту до конца
        path.lineTo(self.x2, self.y2)
        
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "line"

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }

    def set_geometry(self, start_point: QPointF, end_point: QPointF):
        self.x1 = start_point.x()
        self.y1 = start_point.y()
        self.x2 = end_point.x()
        self.y2 = end_point.y()
        self._create_geometry()

class Ellipse(Shape):
    def __init__(self, x, y, w, h, color="black", stroke_width=2):
        super().__init__(color, stroke_width)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        # Отличие только в методе: addEllipse вместо addRect
        path.addEllipse(self.x, self.y, self.w, self.h)
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "ellipse"

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x, self.y],
            "props": {
                "x": self.x, "y": self.y,
                "w": self.w, "h": self.h,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }

    def set_geometry(self, start_point: QPointF, end_point: QPointF):
        self.x = min(start_point.x(), end_point.x())
        self.y = min(start_point.y(), end_point.y())
        self.w = abs(end_point.x() - start_point.x())
        self.h = abs(end_point.y() - start_point.y())
        self._create_geometry()