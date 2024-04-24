from PyQt6.QtWidgets import QApplication
from PathFindVisualizer import MainWindow
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
