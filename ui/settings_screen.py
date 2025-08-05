# ui/settings_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = None # Will be set by DashboardScreen
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Application Settings Screen")
        label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        # Add your settings widgets here later
