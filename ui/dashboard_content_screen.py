# ui/dashboard_content_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class DashboardContentScreen(QWidget):
    """
    A placeholder screen for the main dashboard content.
    This is where summary statistics, quick links, or important alerts could be displayed.
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)

        welcome_label = QLabel("Welcome to Your PharmaCare Dashboard!", self)
        welcome_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(welcome_label)

        info_label = QLabel("Use the sidebar to navigate through different sections.", self)
        info_label.setFont(QFont("Arial", 16))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #34495e;")
        main_layout.addWidget(info_label)

        # You can add more widgets here later, e.g., summary cards, charts, etc.
        # For now, it's a simple welcome message.
