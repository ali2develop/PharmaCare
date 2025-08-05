# ui/signup_screen.py

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy, QToolButton, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Import the User model and DBManager
from models.user import User
from database.db_manager import DBManager

class SignUpScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PharmaCare - Sign Up")
        self.app_signals = None # Will be set by MainWindow
        self.db_manager = None  # Will be set by MainWindow
        self.setup_ui()
        self.password_visible_signup = False
        self.password_visible_confirm = False

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(250, 50, 250, 50)

        signup_card_frame = QFrame(self)
        signup_card_frame.setFrameShape(QFrame.Shape.NoFrame)
        signup_card_frame.setContentsMargins(0, 0, 0, 0)
        signup_card_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        signup_card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        card_layout = QVBoxLayout(signup_card_frame)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(60, 80, 60, 60) # Adjusted top margin

        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(0)

        self.login_tab_button = QPushButton("Login", self)
        self.login_tab_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.login_tab_button.setFixedSize(180, 55)
        self.login_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #555555;
                border: none;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)
        self.login_tab_button.clicked.connect(self._emit_navigate_to_login)

        self.signup_tab_button = QPushButton("Sign Up", self)
        self.signup_tab_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.signup_tab_button.setFixedSize(180, 55)
        self.signup_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        tab_layout.addStretch()
        tab_layout.addWidget(self.login_tab_button)
        tab_layout.addWidget(self.signup_tab_button)
        tab_layout.addStretch()

        card_layout.addLayout(tab_layout)
        card_layout.addSpacing(40)

        create_account_label = QLabel("Create Account", self)
        create_account_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        create_account_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        create_account_label.setStyleSheet("color: #333333;")
        card_layout.addWidget(create_account_label)

        instruction_label = QLabel("Create a new account for your pharmacy staff", self)
        instruction_label.setFont(QFont("Arial", 13))
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: #777777;")
        card_layout.addWidget(instruction_label)
        card_layout.addSpacing(25)

        fullname_label = QLabel("Full Name", self)
        fullname_label.setFont(QFont("Arial", 13))
        fullname_label.setStyleSheet("color: #555555;")
        card_layout.addWidget(fullname_label)

        self.fullname_input = QLineEdit(self)
        self.fullname_input.setPlaceholderText("Enter full name")
        self.fullname_input.setFont(QFont("Arial", 13))
        self.fullname_input.setFixedHeight(50)
        self.fullname_input.setStyleSheet("""
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
        card_layout.addWidget(self.fullname_input)
        card_layout.addSpacing(20)

        email_label = QLabel("Email", self)
        email_label.setFont(QFont("Arial", 13))
        email_label.setStyleSheet("color: #555555;")
        card_layout.addWidget(email_label)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter email address")
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
        self.password_input.setPlaceholderText("Create password")
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

        self.toggle_password_button_signup = QToolButton(self)
        self.toggle_password_button_signup.setText("👁️")
        self.toggle_password_button_signup.setFont(QFont("Segoe UI Emoji", 18))
        self.toggle_password_button_signup.setFixedSize(50, 50)
        self.toggle_password_button_signup.setStyleSheet("""
            QToolButton {
                border: 1px solid #cccccc;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.toggle_password_button_signup.clicked.connect(
            lambda: self.toggle_password_visibility(self.password_input, 'signup')
        )
        password_input_layout.addWidget(self.toggle_password_button_signup)
        card_layout.addLayout(password_input_layout)
        card_layout.addSpacing(20)

        confirm_password_label = QLabel("Confirm Password", self)
        confirm_password_label.setFont(QFont("Arial", 13))
        confirm_password_label.setStyleSheet("color: #555555;")
        card_layout.addWidget(confirm_password_label)

        confirm_password_input_layout = QHBoxLayout()
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setFont(QFont("Arial", 13))
        self.confirm_password_input.setFixedHeight(50)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet("""
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
        confirm_password_input_layout.addWidget(self.confirm_password_input)

        self.toggle_password_button_confirm = QToolButton(self)
        self.toggle_password_button_confirm.setText("👁️")
        self.toggle_password_button_confirm.setFont(QFont("Segoe UI Emoji", 18))
        self.toggle_password_button_confirm.setFixedSize(50, 50)
        self.toggle_password_button_confirm.setStyleSheet("""
            QToolButton {
                border: 1px solid #cccccc;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.toggle_password_button_confirm.clicked.connect(
            lambda: self.toggle_password_visibility(self.confirm_password_input, 'confirm')
        )
        confirm_password_input_layout.addWidget(self.toggle_password_button_confirm)
        card_layout.addLayout(confirm_password_input_layout)
        card_layout.addSpacing(40)

        self.create_account_button = QPushButton("Create Account", self)
        self.create_account_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.create_account_button.setFixedHeight(60)
        self.create_account_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.create_account_button.clicked.connect(self.attempt_signup)
        card_layout.addWidget(self.create_account_button)

        card_layout.addStretch()

        main_layout.addWidget(signup_card_frame)

        self.setStyleSheet("background-color: #f0f2f5;")

    def toggle_password_visibility(self, password_input_field, field_type):
        if field_type == 'signup':
            self.password_visible_signup = not self.password_visible_signup
            is_visible = self.password_visible_signup
            toggle_button = self.toggle_password_button_signup
        else:
            self.password_visible_confirm = not self.password_visible_confirm
            is_visible = self.password_visible_confirm
            toggle_button = self.toggle_password_button_confirm

        if is_visible:
            password_input_field.setEchoMode(QLineEdit.EchoMode.Normal)
            toggle_button.setText("🙈")
        else:
            password_input_field.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_button.setText("👁️")

    def _emit_navigate_to_login(self):
        """Emits a signal to request navigation to the login screen."""
        if self.app_signals:
            self.app_signals.navigate_to_login.emit()

    def show_signup_tab(self):
        """Updates the tab button styles to show 'Sign Up' as active."""
        self.signup_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.login_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #555555;
                border: none;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)

    def attempt_signup(self):
        """
        Handles the Create Account button click event.
        Retrieves user input and attempts to register the user in the database.
        """
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not all([full_name, email, password, confirm_password]):
            self.show_message("Sign Up Error", "Please fill in all fields.")
            return

        if password != confirm_password:
            self.show_message("Sign Up Error", "Passwords do not match.")
            return

        if len(password) < 6:
            self.show_message("Sign Up Error", "Password must be at least 6 characters long.")
            return

        # Check if DBManager instance is available
        if not self.db_manager:
            self.show_message("Database Error", "Database manager not initialized.")
            return

        # Create a User object
        new_user = User(full_name=full_name, email=email, password=password)

        # Attempt to add user to the database
        if self.db_manager.add_user(new_user):
            self.show_message("Sign Up Success", f"Account created for {full_name}! You can now log in.")
            # Clear fields after successful signup
            self.fullname_input.clear()
            self.email_input.clear()
            self.password_input.clear()
            self.confirm_password_input.clear()
            # Navigate to login screen after successful signup
            if self.app_signals:
                self.app_signals.navigate_to_login.emit()
        # Error messages are handled by DBManager's show_error_message

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
    app = QApplication(sys.argv)
    signup_screen = SignUpScreen()
    signup_screen.showMaximized()
    sys.exit(app.exec())
