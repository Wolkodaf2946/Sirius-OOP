from abc import ABC, abstractmethod
import json
from src.logic.io_manager import FileManager
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import QRectF, QSize

class SaveStrategy(ABC):
    @abstractmethod
    def save(self, filename: str, scene):
        pass


class JsonSaveStrategy(SaveStrategy):
    def save(self, filename, scene):
        data = {
            "version": "1.0",
            "scene": {
                "width": scene.width(),
                "height": scene.height()
            },
            "shapes": []
        }

        items = scene.items()[::-1]
        
        for item in items:
            if hasattr(item, "to_dict"):
                data["shapes"].append(item.to_dict())
        
        FileManager.save_project(filename, data)

class ImageSaveStrategy(SaveStrategy):
    def __init__(self, format_name="PNG", background="white"):
        self.format_name = format_name
        self.background = background

    def save(self, filename, scene):
        rect = scene.sceneRect()
        width = int(rect.width())
        height = int(rect.height())

        image = QImage(width, height, QImage.Format_ARGB32)

        if self.background == "transparent":
            image.fill(QColor(0, 0, 0, 0))
        else:
            image.fill(QColor(self.background))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scene.render(painter, QRectF(image.rect()), rect)

        painter.end()

        image.save(filename, self.format_name)