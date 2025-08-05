# ui/login_screen.py

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy, QToolButton, QMessageBox, QCompleter  # Added QCompleter
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QStringListModel  # Added QStringListModel
import bcrypt

# Import the User model and DBManager
from models.user import User
from database.db_manager import DBManager


class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PharmaCare - Login")
        self.app_signals = None
        self.db_manager = None
        self.password_visible = False
        self.completer_model = QStringListModel()  # Initialize completer model
        self.completer = QCompleter(self)  # Initialize QCompleter
        self.setup_ui()
        self.setup_completer()  # Call setup_completer after setup_ui

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(250, 50, 250, 50)

        login_card_frame = QFrame(self)
        login_card_frame.setFrameShape(QFrame.Shape.NoFrame)
        login_card_frame.setContentsMargins(0, 0, 0, 0)
        login_card_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        login_card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        card_layout = QVBoxLayout(login_card_frame)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(60, 150, 60, 60)

        # --- Top Section: Title and Tagline ---
        app_name_label = QLabel("PharmaCare", self)
        app_name_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_label.setStyleSheet("color: #333333;")

        tagline_label = QLabel("Pharmacy Management System", self)
        tagline_label.setFont(QFont("Arial", 14))
        tagline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline_label.setStyleSheet("color: #666666;")

        top_section_layout = QVBoxLayout()
        top_section_layout.addWidget(app_name_label)
        top_section_layout.addWidget(tagline_label)
        top_section_layout.addSpacing(40)

        card_layout.addLayout(top_section_layout)

        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(0)

        self.login_tab_button = QPushButton("Login", self)
        self.login_tab_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.login_tab_button.setFixedSize(180, 55)
        self.login_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.signup_tab_button = QPushButton("Sign Up", self)
        self.signup_tab_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.signup_tab_button.setFixedSize(180, 55)
        self.signup_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #555555;
                border: none;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)
        self.signup_tab_button.clicked.connect(self._emit_navigate_to_signup)

        tab_layout.addStretch()
        tab_layout.addWidget(self.login_tab_button)
        tab_layout.addWidget(self.signup_tab_button)
        tab_layout.addStretch()

        card_layout.addLayout(tab_layout)
        card_layout.addSpacing(40)

        welcome_label = QLabel("Welcome Back", self)
        welcome_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #333333;")
        card_layout.addWidget(welcome_label)

        instruction_label = QLabel("Enter your credentials to access your pharmacy dashboard", self)
        instruction_label.setFont(QFont("Arial", 13))
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: #777777;")
        card_layout.addWidget(instruction_label)
        card_layout.addSpacing(25)

        email_label = QLabel("Email", self)
        email_label.setFont(QFont("Arial", 13))
        email_label.setStyleSheet("color: #555555;")
        card_layout.addWidget(email_label)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFont(QFont("Arial", 13))
        self.email_input.setFixedHeight(50)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 12px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(20)

        password_label = QLabel("Password", self)
        password_label.setFont(QFont("Arial", 13))
        password_label.setStyleSheet("color: #555555;")
        card_layout.addWidget(password_label)

        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFont(QFont("Arial", 13))
        self.password_input.setFixedHeight(50)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 12px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        password_input_layout.addWidget(self.password_input)

        self.toggle_password_button = QToolButton(self)
        self.toggle_password_button.setText("👁️")
        self.toggle_password_button.setFont(QFont("Segoe UI Emoji", 18))
        self.toggle_password_button.setFixedSize(50, 50)
        self.toggle_password_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #cccccc;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.toggle_password_button)

        card_layout.addLayout(password_input_layout)
        card_layout.addSpacing(40)

        self.login_button = QPushButton("Login", self)
        self.login_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.login_button.setFixedHeight(60)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        card_layout.addWidget(self.login_button)

        card_layout.addStretch()

        main_layout.addWidget(login_card_frame)

        self.setStyleSheet("background-color: #f0f2f5;")

    def setup_completer(self):
        """Sets up the QCompleter for the email input field."""
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Allows suggestions anywhere in the string
        self.email_input.setCompleter(self.completer)

    def load_email_suggestions(self):
        """Loads email suggestions from the database into the completer model."""
        if self.db_manager:
            emails = self.db_manager.get_login_emails()
            self.completer_model.setStringList(emails)
            print("Loaded email suggestions:", emails)  # For debugging

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setText("👁️")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setText("🙈")
        self.password_visible = not self.password_visible

    def show_login_tab(self):
        """Updates the tab button styles to show 'Login' as active and loads email suggestions."""
        self.login_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.signup_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #555555;
                border: none;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)
        self.load_email_suggestions()  # Load suggestions when login tab is shown

    def _emit_navigate_to_signup(self):
        """Emits a signal to request navigation to the signup screen."""
        if self.app_signals:
            self.app_signals.navigate_to_signup.emit()

    def attempt_login(self):
        """
        Handles the Login button click event.
        Retrieves user input and attempts to authenticate the user against the database.
        """
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.show_message("Login Error", "Please enter both email and password.")
            return

        # Check if DBManager instance is available
        if not self.db_manager:
            self.show_message("Database Error", "Database manager not initialized.")
            return

        # Attempt to retrieve user from the database
        user_data = self.db_manager.get_user_by_email(email)

        if user_data:
            # User found, now verify password
            stored_hashed_password = user_data[3].encode('utf-8')  # Hashed password is at index 3
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                # Login successful, emit signal with user's full name and email
                self.show_message("Login Success", f"Welcome back, {user_data[1]}!")

                # New: Add email to login history
                self.db_manager.add_login_email(email)
                self.load_email_suggestions()  # Refresh completer model to include new email

                # Clear fields after successful login
                self.email_input.clear()
                self.password_input.clear()
                if self.app_signals:
                    self.app_signals.login_successful.emit(user_data[1], user_data[2])
            else:
                self.show_message("Login Failed", "Invalid email or password.")
        else:
            # User not found
            self.show_message("Login Failed", "Invalid email or password.")

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f0f2f5;
                font-family: Arial;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        msg_box.exec()


if __name__ == "__main__":
    import sys
    from database.db_manager import DBManager
    from models.user import User  # Import User for standalone test

    app = QApplication(sys.argv)
    login_screen = LoginScreen()
    # For standalone test, create a dummy DBManager and add some emails
    test_db_manager = DBManager("test_login_history.db")
    test_db_manager.add_user(User("Test User", "test@example.com", "password123"))
    test_db_manager.add_user(User("Another User", "another@domain.com", "securepass"))
    test_db_manager.add_login_email("test@example.com")
    test_db_manager.add_login_email("previous@email.com")
    login_screen.db_manager = test_db_manager
    login_screen.load_email_suggestions()  # Manually load for standalone test

    login_screen.showMaximized()
    sys.exit(app.exec())
