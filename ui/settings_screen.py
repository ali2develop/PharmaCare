# ui/settings_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SettingsScreen(QWidget):
    """
    UI for managing application settings. This is a placeholder screen
    that can be expanded to include various configurable options.
    """
    def __init__(self):
        super().__init__()
        self.db_manager = None # Will be set by DashboardScreen
        self.setup_ui()

    def setup_ui(self):
        """Sets up the layout and widgets for the settings screen."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        header_label = QLabel("Application Settings", self)
        header_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(header_label)

        info_label = QLabel("This is where you can configure various application settings.", self)
        info_label.setFont(QFont("Arial", 16))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #34495e;")
        main_layout.addWidget(info_label)

        # Placeholder for future settings options
        # Example:
        # self.theme_setting_label = QLabel("Theme:", self)
        # self.theme_combo_box = QComboBox(self)
        # self.theme_combo_box.addItem("Light")
        # self.theme_combo_box.addItem("Dark")
        # main_layout.addWidget(self.theme_setting_label)
        # main_layout.addWidget(self.theme_combo_box)

        main_layout.addStretch() # Push content to the top/center

        self.setStyleSheet("background-color: #f0f2f5;")

    def set_db_manager(self, db_manager):
        """Sets the DBManager instance for this screen."""
        self.db_manager = db_manager
        # No data loading needed for this basic placeholder, but useful for future features


if __name__ == "__main__":
    import sys
    # For standalone testing of SettingsScreen
    app = QApplication(sys.argv)
    settings_screen = SettingsScreen()
    settings_screen.showMaximized()
    sys.exit(app.exec())
