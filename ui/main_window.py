# ui/main_window.py

import sys
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Import your screen classes
from ui.login_screen import LoginScreen
from ui.signup_screen import SignUpScreen

# Import database manager
from database.db_manager import DBManager

# Import styles
from styles.app_styles import APP_STYLES

class AppSignals(QObject):
    """
    A QObject to define custom signals for screen navigation and application-wide events.
    This helps in decoupling screen logic from the main window logic.
    """
    navigate_to_login = pyqtSignal()
    navigate_to_signup = pyqtSignal()
    login_successful = pyqtSignal()
    # Add other signals as needed, e.g., logout_requested, show_dashboard, etc.

class MainWindow(QMainWindow):
    """
    The main application window that manages different screens (Login, Sign Up, Dashboard, etc.).
    It uses a QStackedWidget to switch between these screens.
    """
    def __init__(self):
        """
        Initializes the MainWindow, sets up the stacked widget, and connects screens.
        """
        super().__init__()
        self.setWindowTitle("PharmaCare Management System")
        self.setMinimumSize(1024, 768) # Set a reasonable minimum size for a desktop app
        self.showMaximized() # Start in full screen

        # Initialize database manager
        self.db_manager = DBManager()

        # Apply global styles
        QApplication.instance().setStyleSheet(APP_STYLES)

        # Initialize the QStackedWidget to hold different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create a signal object to pass around
        self.app_signals = AppSignals()

        # Create instances of your screens
        self.login_screen = LoginScreen()
        self.signup_screen = SignUpScreen()
        # self.dashboard_screen = DashboardScreen() # Will be added later

        # Pass the signal object and DB manager to screens
        self.login_screen.app_signals = self.app_signals
        self.login_screen.db_manager = self.db_manager # Pass DB manager to screens
        self.signup_screen.app_signals = self.app_signals
        self.signup_screen.db_manager = self.db_manager # Pass DB manager to screens

        # Connect signals from screens to main window methods
        self.app_signals.navigate_to_signup.connect(self.show_signup_screen)
        self.app_signals.navigate_to_login.connect(self.show_login_screen)
        self.app_signals.login_successful.connect(self.show_dashboard_screen) # Connect login success to dashboard

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.login_screen)  # Index 0
        self.stacked_widget.addWidget(self.signup_screen) # Index 1
        # self.stacked_widget.addWidget(self.dashboard_screen) # Add dashboard when ready

        # Initially show the login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Switches the stacked widget to display the login screen."""
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.login_screen.show_login_tab() # Update tab styles

    def show_signup_screen(self):
        """Switches the stacked widget to display the sign-up screen."""
        self.stacked_widget.setCurrentWidget(self.signup_screen)
        self.signup_screen.show_signup_tab() # Update tab styles

    def show_dashboard_screen(self):
        """
        Placeholder method to show the dashboard screen.
        Will be implemented when dashboard screen is ready.
        """
        QMessageBox.information(self, "Navigation", "Login successful! Dashboard coming soon.")
        # When dashboard is ready:
        # self.stacked_widget.setCurrentWidget(self.dashboard_screen)
        # self.dashboard_screen.load_data() # Example: load dashboard data
