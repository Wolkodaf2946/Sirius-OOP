import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QRadioButton, QGroupBox, QLabel,
    QHeaderView)

from PySide6.QtCore import Qt

class DemoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Задаем заголовок и размер окна
        self.setWindowTitle("Демонстрация PySide6")
        self.setGeometry(100, 100, 500, 400)

        # 1. Главный макет (Вертикальный)
        main_layout = QVBoxLayout()

        # 2. Группа для ввода данных (Горизонтальный макет)
        input_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ФИО сотрудника")
        input_layout.addWidget(self.name_input)

        # 3. Группа для опций
        options_layout = QHBoxLayout()

        # 3.1. QCheckBox
        self.status_check = QCheckBox("Активен")
        self.status_check.setChecked(True)
        options_layout.addWidget(self.status_check)

        # 3.2. QRadioButton (внутри QGroupBox для объединения)
        self.dept_group = QGroupBox("Отдел")
        dept_layout = QHBoxLayout()  # Макет для самой группы
        self.rb_dev = QRadioButton("Разработка")
        self.rb_sales = QRadioButton("Продажи")
        self.rb_hr = QRadioButton("HR")
        self.rb_dev.setChecked(True)  # Выбор по умолчанию
        dept_layout.addWidget(self.rb_dev)
        dept_layout.addWidget(self.rb_sales)
        dept_layout.addWidget(self.rb_hr)
        self.dept_group.setLayout(dept_layout)
        options_layout.addWidget(self.dept_group)

        # 4. Кнопка добавления
        self.add_button = QPushButton("Добавить в таблицу")

        # Подключаем сигнал 'clicked' к слоту 'add_row_to_table'
        self.add_button.clicked.connect(self.add_row_to_table)

        # 5. Таблица (QTableWidget)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ФИО", "Статус", "Отдел"])

        # Настраиваем растягивание колонок

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # Собираем все в главный макет

        main_layout.addLayout(input_layout)
        main_layout.addLayout(options_layout)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.table)  # Таблица займет все оставшееся место

        # Устанавливаем главный макет для окна

        self.setLayout(main_layout)

    # "Слот", который вызывается при нажатии кнопки
    def add_row_to_table(self):
        # Получаем данные из виджетов

        # 1. Из QLineEdit
        name = self.name_input.text()

        if not name:  # Простая валидация
            self.name_input.setPlaceholderText("СНАЧАЛА ВВЕДИТЕ ИМЯ!")
            return

        # 2. Из QCheckBox
        status = "Активен" if self.status_check.isChecked() else "Неактивен"

        # 3. Из QRadioButtons
        department = "Неизвестно"
        if self.rb_dev.isChecked():
            department = "Разработка"
        elif self.rb_sales.isChecked():
            department = "Продажи"
        elif self.rb_hr.isChecked():
            department = "HR"

        # Добавляем новую строку в таблицу
        current_row_count = self.table.rowCount()
        self.table.insertRow(current_row_count)

        # Создаем ячейки QTableWidgetItem
        name_item = QTableWidgetItem(name)
        status_item = QTableWidgetItem(status)
        dept_item = QTableWidgetItem(department)

        # Запрещаем редактирование ячеек (по желанию)
        # name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        # status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
        # dept_item.setFlags(dept_item.flags() & ~Qt.ItemIsEditable)

        # Заполняем строку
        self.table.setItem(current_row_count, 0, name_item)
        self.table.setItem(current_row_count, 1, status_item)
        self.table.setItem(current_row_count, 2, dept_item)

        # Очищаем поле ввода и сбрасываем placeholder
        self.name_input.clear()
        self.name_input.setPlaceholderText("Введите ФИО сотрудника")

# Точка входа в приложение
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoApp()
    window.show()
    sys.exit(app.exec())