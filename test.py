class CircleWidget(QWidget):
    def paintEvent(self, event):
        # QPainter - наш "холст"
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Сглаживание

        # Рисуем красный круг в центре
        painter.setBrush(Qt.red)
        painter.drawEllipse(self.rect().center(), 50, 50)