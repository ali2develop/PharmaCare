# main.py

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow # Import the MainWindow

def main():
    """
    The main function to initialize and run the PharmaCare application.
    """
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show() # Show the main window
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

