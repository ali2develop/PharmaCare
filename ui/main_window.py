# ui/main_window.py

import sys
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Import your screen classes
from ui.login_screen import LoginScreen
from ui.signup_screen import SignUpScreen
from ui.dashboard_screen import DashboardScreen # Import the new DashboardScreen

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
    login_successful = pyqtSignal(str, str) # Modified to pass user_name, user_email
    logout_requested = pyqtSignal() # New signal for logout
    # Add other signals as needed, e.g., show_dashboard, etc.

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
        self.dashboard_screen = DashboardScreen() # Instantiate DashboardScreen

        # Pass the signal object and DB manager to screens
        self.login_screen.app_signals = self.app_signals
        self.login_screen.db_manager = self.db_manager # Pass DB manager to login screen
        self.signup_screen.app_signals = self.app_signals
        self.signup_screen.db_manager = self.db_manager # Pass DB manager to signup screen
        self.dashboard_screen.app_signals = self.app_signals # Pass signals to dashboard
        self.dashboard_screen.set_db_manager(self.db_manager) # Pass DB manager to dashboard and its sub-screens

        # Connect signals from screens to main window methods
        self.app_signals.navigate_to_signup.connect(self.show_signup_screen)
        self.app_signals.navigate_to_login.connect(self.show_login_screen)
        # Connect login_successful to show_dashboard_screen, passing user info
        self.app_signals.login_successful.connect(self.show_dashboard_screen)
        # Connect logout_requested to show_login_screen
        self.app_signals.logout_requested.connect(self.show_login_screen)


        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.login_screen)  # Index 0
        self.stacked_widget.addWidget(self.signup_screen) # Index 1
        self.stacked_widget.addWidget(self.dashboard_screen) # Index 2

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

    def show_dashboard_screen(self, user_name, user_email):
        """
        Switches to the dashboard screen and updates user information.
        """
        self.dashboard_screen.set_user_info(user_name, user_email)
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
        # Optionally, you might want to reset the dashboard to its default view
        self.dashboard_screen.switch_screen(0, self.dashboard_screen.dashboard_button)
