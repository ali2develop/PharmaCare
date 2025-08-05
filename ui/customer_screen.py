# ui/customer_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
    QSizePolicy, QApplication
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal # Ensure pyqtSignal is imported
from models.customer import Customer

class CustomerScreen(QWidget):
    # Define a signal that will be emitted when customer data changes
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.selected_customer_id = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Customer Management")
        header_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        input_frame = QFrame(self)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                /* Removed box-shadow */
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        form_layout = QVBoxLayout(input_frame)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(10)

        self.name_layout, self.name_input_widget = self._create_labeled_input("Customer Name:", "Enter customer's full name")
        self.phone_layout, self.phone_input_widget = self._create_labeled_input("Phone Number:", "Enter phone number (e.g., 123-456-7890)")
        self.email_layout, self.email_input_widget = self._create_labeled_input("Email Address:", "Enter email address (optional)")
        self.address_layout, self.address_input_widget = self._create_labeled_input("Address:", "Enter customer's address (optional)", is_multiline=True)

        form_layout.addLayout(self.name_layout)
        form_layout.addLayout(self.phone_layout)
        form_layout.addLayout(self.email_layout)
        form_layout.addLayout(self.address_layout)

        button_layout = QHBoxLayout()
        self.add_button = self._create_button("Add Customer", "#28a745")
        self.update_button = self._create_button("Update Customer", "#007bff")
        self.clear_button = self._create_button("Clear Form", "#6c757d")

        self.add_button.clicked.connect(self.add_customer)
        self.update_button.clicked.connect(self.update_customer)
        self.update_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_form)

        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)

        main_layout.addWidget(input_frame)

        search_frame = QFrame(self)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                /* Removed box-shadow */
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(25, 15, 25, 15)
        search_layout.setSpacing(10)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search by name, phone, or email...")
        self.search_input.textChanged.connect(self.search_customers)
        search_layout.addWidget(self.search_input)

        main_layout.addWidget(search_frame)

        self.customer_table = QTableWidget(self)
        self.customer_table.setColumnCount(6)
        self.customer_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Address", "Created At"
        ])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customer_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.customer_table.itemSelectionChanged.connect(self.load_selected_customer_to_form)
        self.customer_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f0f2f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                color: #34495e;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e0f7fa;
                color: #2c3e50;
            }
        """)
        main_layout.addWidget(self.customer_table)

        delete_button_layout = QHBoxLayout()
        self.delete_button = self._create_button("Delete Selected Customer", "#dc3545")
        self.delete_button.clicked.connect(self.delete_customer)
        self.delete_button.setEnabled(False)
        delete_button_layout.addStretch()
        delete_button_layout.addWidget(self.delete_button)
        delete_button_layout.addStretch()
        main_layout.addLayout(delete_button_layout)

    def _create_labeled_input(self, label_text, placeholder_text, is_multiline=False):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        h_layout.addWidget(label)

        if is_multiline:
            text_input = QLineEdit(self)
            text_input.setFixedHeight(80)
        else:
            text_input = QLineEdit(self)
            text_input.setFixedHeight(40)

        text_input.setPlaceholderText(placeholder_text)
        h_layout.addWidget(text_input)
        h_layout.addStretch()
        return h_layout, text_input

    def _create_button(self, text, color, font_size=14, padding="12px 25px"):
        button = QPushButton(text)
        button.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: {padding};
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.2)};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        return button

    def _darken_color(self, hex_color, factor=0.1):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}"

    def set_db_manager(self, db_manager):
        self.db_manager = db_manager
        self.load_customers()

    def load_customers(self):
        if not self.db_manager: return
        customers = self.db_manager.get_all_customers()
        self.customer_table.setRowCount(len(customers))

        for row_idx, cust in enumerate(customers):
            self.customer_table.setItem(row_idx, 0, QTableWidgetItem(str(cust.id)))
            self.customer_table.setItem(row_idx, 1, QTableWidgetItem(cust.name))
            self.customer_table.setItem(row_idx, 2, QTableWidgetItem(cust.phone if cust.phone else ""))
            self.customer_table.setItem(row_idx, 3, QTableWidgetItem(cust.email if cust.email else ""))
            self.customer_table.setItem(row_idx, 4, QTableWidgetItem(cust.address if cust.address else ""))
            self.customer_table.setItem(row_idx, 5, QTableWidgetItem(cust.created_at if cust.created_at else ""))

        self.customer_table.resizeColumnsToContents()
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.clear_form()

    def add_customer(self):
        name = self.name_input_widget.text().strip()
        phone = self.phone_input_widget.text().strip()
        email = self.email_input_widget.text().strip()
        address = self.address_input_widget.text().strip()

        if not name or not phone:
            self.show_message("Input Error", "Customer Name and Phone Number are required.")
            return

        new_customer = Customer(name=name, phone=phone, email=email, address=address)

        if self.db_manager.add_customer(new_customer):
            self.show_message("Success", f"Customer '{name}' added successfully.")
            self.load_customers()
            self.data_changed.emit() # Emit signal after data change
        # Error messages are handled by DBManager

    def update_customer(self):
        if self.selected_customer_id is None:
            self.show_message("Selection Error", "Please select a customer from the table to update.")
            return

        name = self.name_input_widget.text().strip()
        phone = self.phone_input_widget.text().strip()
        email = self.email_input_widget.text().strip()
        address = self.address_input_widget.text().strip()

        if not name or not phone:
            self.show_message("Input Error", "Customer Name and Phone Number are required.")
            return

        updated_customer = Customer(
            customer_id=self.selected_customer_id,
            name=name, phone=phone, email=email, address=address
        )

        if self.db_manager.update_customer(updated_customer):
            self.show_message("Success", f"Customer '{name}' updated successfully.")
            self.load_customers()
            self.data_changed.emit() # Emit signal after data change
        # Error messages are handled by DBManager

    def delete_customer(self):
        if self.selected_customer_id is None:
            self.show_message("Selection Error", "Please select a customer from the table to delete.")
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Deletion")
        msg_box.setText(f"Are you sure you want to delete customer ID {self.selected_customer_id}?")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #f0f2f5; font-family: Arial; }
            QMessageBox QLabel { color: #333333; font-size: 14px; }
            QMessageBox QPushButton {
                background-color: #dc3545; color: white; border: none;
                border-radius: 5px; padding: 8px 15px; min-width: 80px;
            }
            QMessageBox QPushButton:hover { background-color: #c82333; }
            QMessageBox QPushButton#No {
                background-color: #6c757d;
            }
            QMessageBox QPushButton#No:hover {
                background-color: #5a6268;
            }
        """)
        ret = msg_box.exec()

        if ret == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_customer(self.selected_customer_id):
                self.show_message("Success", f"Customer ID {self.selected_customer_id} deleted successfully.")
                self.load_customers()
                self.data_changed.emit() # Emit signal after data change
            # Error messages are handled by DBManager
        else:
            self.show_message("Cancelled", "Deletion cancelled.")

    def load_selected_customer_to_form(self):
        selected_rows = self.customer_table.selectedItems()
        if not selected_rows:
            self.clear_form()
            self.selected_customer_id = None
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.add_button.setEnabled(True)
            return

        row = selected_rows[0].row()
        self.selected_customer_id = int(self.customer_table.item(row, 0).text())

        self.name_input_widget.setText(self.customer_table.item(row, 1).text())
        self.phone_input_widget.setText(self.customer_table.item(row, 2).text())
        self.email_input_widget.setText(self.customer_table.item(row, 3).text())
        self.address_input_widget.setText(self.customer_table.item(row, 4).text())

        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.add_button.setEnabled(False)

    def clear_form(self):
        self.name_input_widget.clear()
        self.phone_input_widget.clear()
        self.email_input_widget.clear()
        self.address_input_widget.clear()
        self.selected_customer_id = None
        self.customer_table.clearSelection()

        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def search_customers(self):
        search_text = self.search_input.text().strip().lower()
        for row in range(self.customer_table.rowCount()):
            name_match = search_text in self.customer_table.item(row, 1).text().lower()
            phone_match = search_text in self.customer_table.item(row, 2).text().lower()
            email_match = search_text in self.customer_table.item(row, 3).text().lower()
            self.customer_table.setRowHidden(row, not (name_match or phone_match or email_match))

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information if "Success" in title or "Cancelled" in title else QMessageBox.Icon.Warning)
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
    from models.customer import Customer
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    db_manager = DBManager("test_pharmacy_customer.db")

    db_manager.add_customer(Customer(name="Alice Wonderland", phone="111-222-3333", email="alice@example.com", address="1 Wonderland Lane"))
    db_manager.add_customer(Customer(name="Bob The Builder", phone="444-555-6666", email="bob@example.com", address="Construction Site"))
    db_manager.add_customer(Customer(name="Charlie Chaplin", phone="777-888-9999", email="charlie@example.com", address="Hollywood Hills"))

    customer_screen = CustomerScreen()
    customer_screen.set_db_manager(db_manager)
    customer_screen.showMaximized()
    sys.exit(app.exec())
