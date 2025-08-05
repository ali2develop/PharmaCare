# ui/dashboard_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QFrame, QSizePolicy, QApplication
)
from PyQt6.QtGui import QFont, QIcon, QPixmap  # Ensure QPixmap is imported
from PyQt6.QtCore import Qt, pyqtSignal, QSize

# Import screens
from ui.dashboard_content_screen import DashboardContentScreen
from ui.medicine_screen import MedicineScreen
from ui.customer_screen import CustomerScreen
from ui.billing_screen import BillingScreen
from ui.settings_screen import SettingsScreen
from ui.reports_screen import ReportsScreen


class DashboardScreen(QWidget):
    """
    The main dashboard screen for the PharmaCare application.
    It features a sidebar for navigation and a main content area
    managed by a QStackedWidget.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PharmaCare - Dashboard")
        self.app_signals = None
        self.db_manager = None
        self.current_user = None

        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the main layout of the dashboard, including the sidebar and content area.
        """
        main_h_layout = QHBoxLayout(self)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar_frame = QFrame(self)
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50; /* Dark blue-gray */
                border-right: 1px solid #34495e;
            }
            QPushButton {
                background-color: transparent;
                color: #ecf0f1; /* Light gray text */
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px; /* No rounded corners for sidebar buttons */
            }
            QPushButton:hover {
                background-color: #34495e; /* Slightly lighter on hover */
            }
            QPushButton:checked { /* Style for active/selected button */
                background-color: #007bff; /* Primary blue */
                border-left: 5px solid #28a745; /* Green accent for active tab */
            }
            QLabel#user_name_label {
                color: #ecf0f1;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
            }
            QLabel#user_email_label {
                color: #bdc3c7;
                font-size: 12px;
                padding: 0px 15px 15px 15px;
                text-align: center;
            }
        """)
        self.sidebar_frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- App Logo/Name at the top of the sidebar (NOW IMAGE LOGO) ---
        self.app_logo_label = QLabel(
            self.sidebar_frame)  # Changed to self.app_logo_label for potential future reference

        # Load the image
        pixmap = QPixmap("assets/icon.png")
        if pixmap.isNull():
            print("Error: Could not load assets/icon.png. Ensure the path is correct.")
            # Fallback to text if image fails to load
            self.app_logo_label.setText("PharmaCare")
            self.app_logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        else:
            # Scale the pixmap to fit within a certain size while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.app_logo_label.setPixmap(scaled_pixmap)
            self.app_logo_label.setFixedSize(scaled_pixmap.size())  # Set label size to pixmap size

        self.app_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Keep the existing padding and background color for the logo area
        self.app_logo_label.setStyleSheet("padding: 20px 0; background-color: #34495e;")
        sidebar_layout.addWidget(self.app_logo_label)
        sidebar_layout.addSpacing(20)

        # User Info Section (placeholder)
        self.user_name_label = QLabel("Welcome, User!", self.sidebar_frame)
        self.user_name_label.setObjectName("user_name_label")
        self.user_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.user_name_label)

        self.user_email_label = QLabel("user@example.com", self.sidebar_frame)
        self.user_email_label.setObjectName("user_email_label")
        self.user_email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.user_email_label)
        sidebar_layout.addSpacing(30)

        # Navigation Buttons
        self.dashboard_button = self._create_sidebar_button("📊 Dashboard", "dashboard")
        self.medicines_button = self._create_sidebar_button("💊 Medicines", "medicines")
        self.customers_button = self._create_sidebar_button("👥 Customers", "customers")
        self.billing_button = self._create_sidebar_button("🧾 Billing", "billing")
        self.reports_button = self._create_sidebar_button("📈 Reports", "reports")
        self.settings_button = self._create_sidebar_button("⚙️ Settings", "settings")

        sidebar_layout.addWidget(self.dashboard_button)
        sidebar_layout.addWidget(self.medicines_button)
        sidebar_layout.addWidget(self.customers_button)
        sidebar_layout.addWidget(self.billing_button)
        sidebar_layout.addWidget(self.reports_button)
        sidebar_layout.addWidget(self.settings_button)

        sidebar_layout.addStretch()  # Pushes buttons to the top

        # Logout Button
        self.logout_button = self._create_sidebar_button("🚪 Logout", "logout")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; /* Red for logout */
                color: white;
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.logout_button.clicked.connect(self._emit_logout)
        sidebar_layout.addWidget(self.logout_button)

        main_h_layout.addWidget(self.sidebar_frame)

        # --- Content Area ---
        self.content_stacked_widget = QStackedWidget(self)
        self.content_stacked_widget.setStyleSheet("background-color: #f8f9fa;")

        # Create instances of content screens
        self.dashboard_content = DashboardContentScreen()
        self.medicines_content = MedicineScreen()
        self.customers_content = CustomerScreen()
        self.billing_content = BillingScreen()
        self.reports_content = ReportsScreen()
        self.settings_content = SettingsScreen()

        # Add content screens to the stacked widget (adjusting indices)
        self.content_stacked_widget.addWidget(self.dashboard_content)  # Index 0
        self.content_stacked_widget.addWidget(self.medicines_content)  # Index 1
        self.content_stacked_widget.addWidget(self.customers_content)  # Index 2
        self.content_stacked_widget.addWidget(self.billing_content)  # Index 3
        self.content_stacked_widget.addWidget(self.reports_content)  # Index 4
        self.content_stacked_widget.addWidget(self.settings_content)  # Index 5

        main_h_layout.addWidget(self.content_stacked_widget)

        # Connect sidebar buttons to switch content (adjusting indices)
        self.dashboard_button.clicked.connect(lambda: self.switch_screen(0, self.dashboard_button))
        self.medicines_button.clicked.connect(lambda: self.switch_screen(1, self.medicines_button))
        self.customers_button.clicked.connect(lambda: self.switch_screen(2, self.customers_button))
        self.billing_button.clicked.connect(lambda: self.switch_screen(3, self.billing_button))
        self.reports_button.clicked.connect(lambda: self.switch_screen(4, self.reports_button))
        self.settings_button.clicked.connect(lambda: self.switch_screen(5, self.settings_button))

        # Set initial active button and screen
        self.active_button = None
        self.switch_screen(0, self.dashboard_button)

        # --- Connect data change signals for auto-updates ---
        self.medicines_content.data_changed.connect(self.billing_content.load_available_medicines)
        self.customers_content.data_changed.connect(self.billing_content.load_available_customers)

        self.medicines_content.data_changed.connect(self.dashboard_content.load_dashboard_stats)
        self.customers_content.data_changed.connect(self.dashboard_content.load_dashboard_stats)
        self.billing_content.sale_processed.connect(self.dashboard_content.load_dashboard_stats)

    def _create_sidebar_button(self, text, object_name):
        """Helper to create a styled sidebar button."""
        button = QPushButton(text, self.sidebar_frame)
        button.setObjectName(object_name)
        button.setCheckable(True)
        return button

    def _create_placeholder_screen(self, text):
        """Helper to create a simple placeholder widget for content areas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(text)
        label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #34495e;")
        layout.addWidget(label)
        return widget

    def switch_screen(self, index, clicked_button):
        """
        Switches the content in the QStackedWidget and updates sidebar button styles.
        Also triggers data refresh for the dashboard if it's being displayed,
        and generates reports if the reports screen is displayed.
        """
        self.content_stacked_widget.setCurrentIndex(index)

        # If the dashboard screen is being shown, load its stats
        if index == 0:
            self.dashboard_content.load_dashboard_stats()
        # If the reports screen is being shown, generate its default report
        elif index == 4:
            self.reports_content.generate_report()

        # Update button styles
        if self.active_button:
            self.active_button.setChecked(False)
        clicked_button.setChecked(True)
        self.active_button = clicked_button

    def _emit_logout(self):
        """Emits a signal to request application logout."""
        if self.app_signals:
            self.app_signals.logout_requested.emit()

    def set_user_info(self, user_name, user_email):
        """Updates the user information displayed in the sidebar."""
        self.user_name_label.setText(f"Welcome, {user_name}!")
        self.user_email_label.setText(user_email)

    def set_db_manager(self, db_manager):
        """Sets the DBManager instance and passes it to sub-screens.
        Also triggers initial dashboard stats load.
        """
        self.db_manager = db_manager
        # Pass DBManager to all content screens
        self.dashboard_content.set_db_manager(db_manager)
        self.medicines_content.set_db_manager(db_manager)
        self.customers_content.set_db_manager(db_manager)
        self.billing_content.set_db_manager(db_manager)
        self.reports_content.set_db_manager(db_manager)
        self.settings_content.db_manager = db_manager

        # Ensure dashboard stats are loaded when DBManager is first set
        self.dashboard_content.load_dashboard_stats()
