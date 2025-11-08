# main.py
from PySide6.QtWidgets import QApplication
from ui import MainWindow
import sys
import os

if __name__ == "__main__":
    # Ensure working dir is the script directory (helps with PyInstaller bundling)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
