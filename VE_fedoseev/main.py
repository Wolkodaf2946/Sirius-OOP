import sys
from PySide6.QtWidgets import QApplication
from src.app import VectorEditorWindow

def main():
    app = QApplication(sys.argv)
    window = VectorEditorWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()