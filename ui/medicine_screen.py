# ui/medicine_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QComboBox,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem, QApplication
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QDate, pyqtSignal  # Import pyqtSignal
from models.medicine import Medicine


class MedicineScreen(QWidget):
    # Define a signal that will be emitted when medicine data changes
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.selected_medicine_id = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Medicine Management")
        header_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        input_frame = QFrame(self)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
            }
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        form_layout = QVBoxLayout(input_frame)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(10)

        self.name_layout, self.name_input_widget = self._create_labeled_input("Medicine Name:", "Enter medicine name")
        self.brand_layout, self.brand_input_widget = self._create_labeled_input("Brand:", "Enter brand name (optional)")
        self.category_layout, self.category_input_widget = self._create_labeled_input("Category:",
                                                                                      "Enter category (e.g., Pain Relief)")
        self.price_layout, self.price_input_widget = self._create_labeled_input("Price:", "Enter price",
                                                                                is_numeric=True)
        self.stock_layout, self.stock_input_widget = self._create_labeled_input("Stock Quantity:",
                                                                                "Enter stock quantity", is_numeric=True)
        self.low_stock_alert_layout, self.low_stock_alert_input_widget = self._create_labeled_input("Low Stock Alert:",
                                                                                                    "Set alert threshold (default 10)",
                                                                                                    is_numeric=True,
                                                                                                    default_text="10")

        expiry_date_layout = QHBoxLayout()
        expiry_date_label = QLabel("Expiry Date:")
        expiry_date_label.setFixedWidth(120)
        expiry_date_layout.addWidget(expiry_date_label)
        self.expiry_date_edit = QDateEdit(self)
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        self.expiry_date_edit.setMinimumDate(QDate.currentDate())
        expiry_date_layout.addWidget(self.expiry_date_edit)
        expiry_date_layout.addStretch()
        form_layout.addLayout(expiry_date_layout)

        self.description_layout, self.description_input_widget = self._create_labeled_input("Description:",
                                                                                            "Enter description (optional)",
                                                                                            is_multiline=True)

        form_layout.addLayout(self.name_layout)
        form_layout.addLayout(self.brand_layout)
        form_layout.addLayout(self.category_layout)
        form_layout.addLayout(self.price_layout)
        form_layout.addLayout(self.stock_layout)
        form_layout.addLayout(self.low_stock_alert_layout)
        form_layout.addLayout(self.description_layout)

        button_layout = QHBoxLayout()
        self.add_button = self._create_button("Add Medicine", "#28a745")
        self.update_button = self._create_button("Update Medicine", "#007bff")
        self.clear_button = self._create_button("Clear Form", "#6c757d")

        self.add_button.clicked.connect(self.add_medicine)
        self.update_button.clicked.connect(self.update_medicine)
        self.update_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_form)

        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)

        main_layout.addWidget(input_frame)

        search_filter_frame = QFrame(self)
        search_filter_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }
        """)
        search_filter_layout = QHBoxLayout(search_filter_frame)
        search_filter_layout.setContentsMargins(25, 15, 25, 15)
        search_filter_layout.setSpacing(10)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search by name, brand, or category...")
        self.search_input.textChanged.connect(self.search_medicines)
        search_filter_layout.addWidget(self.search_input)

        self.filter_combo = QComboBox(self)
        self.filter_combo.addItem("All Medicines")
        self.filter_combo.addItem("Low Stock")
        self.filter_combo.addItem("Expired / Expiring Soon")
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        search_filter_layout.addWidget(self.filter_combo)

        main_layout.addWidget(search_filter_frame)

        self.medicine_table = QTableWidget(self)
        self.medicine_table.setColumnCount(10)
        self.medicine_table.setHorizontalHeaderLabels([
            "ID", "Name", "Brand", "Category", "Price", "Stock",
            "Low Alert", "Expiry Date", "Description", "Created At"
        ])
        self.medicine_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.medicine_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.medicine_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.medicine_table.itemSelectionChanged.connect(self.load_selected_medicine_to_form)
        self.medicine_table.setStyleSheet("""
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
        main_layout.addWidget(self.medicine_table)

        delete_button_layout = QHBoxLayout()
        self.delete_button = self._create_button("Delete Selected Medicine", "#dc3545")
        self.delete_button.clicked.connect(self.delete_medicine)
        self.delete_button.setEnabled(False)
        delete_button_layout.addStretch()
        delete_button_layout.addWidget(self.delete_button)
        delete_button_layout.addStretch()
        main_layout.addLayout(delete_button_layout)

    def _create_labeled_input(self, label_text, placeholder_text, is_numeric=False, is_multiline=False,
                              default_text=""):
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
        if is_numeric:
            from PyQt6.QtGui import QDoubleValidator
            validator = QDoubleValidator(0.0, 1000000.0, 2)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            text_input.setValidator(validator)
            if default_text:
                text_input.setText(default_text)
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
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}"

    def create_numeric_validator(self):
        from PyQt6.QtGui import QDoubleValidator
        validator = QDoubleValidator(0.0, 1000000.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        return validator

    def set_db_manager(self, db_manager):
        self.db_manager = db_manager
        self.load_medicines()

    def load_medicines(self):
        if not self.db_manager: return
        medicines = self.db_manager.get_all_medicines()
        self.medicine_table.setRowCount(len(medicines))

        for row_idx, med in enumerate(medicines):
            self.medicine_table.setItem(row_idx, 0, QTableWidgetItem(str(med.id)))
            self.medicine_table.setItem(row_idx, 1, QTableWidgetItem(med.name))
            self.medicine_table.setItem(row_idx, 2, QTableWidgetItem(med.brand if med.brand else ""))
            self.medicine_table.setItem(row_idx, 3, QTableWidgetItem(med.category if med.category else ""))
            self.medicine_table.setItem(row_idx, 4, QTableWidgetItem(f"{med.price:.2f}"))
            self.medicine_table.setItem(row_idx, 5, QTableWidgetItem(str(med.stock)))
            self.medicine_table.setItem(row_idx, 6, QTableWidgetItem(str(med.low_stock_alert)))
            self.medicine_table.setItem(row_idx, 7, QTableWidgetItem(med.expiry_date if med.expiry_date else ""))
            self.medicine_table.setItem(row_idx, 8, QTableWidgetItem(med.description if med.description else ""))
            self.medicine_table.setItem(row_idx, 9, QTableWidgetItem(med.created_at if med.created_at else ""))

        self.medicine_table.resizeColumnsToContents()
        self.medicine_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.clear_form()

    def add_medicine(self):
        name = self.name_input_widget.text().strip()
        brand = self.brand_input_widget.text().strip()
        category = self.category_input_widget.text().strip()
        price_text = self.price_input_widget.text().strip()
        stock_text = self.stock_input_widget.text().strip()
        low_stock_alert_text = self.low_stock_alert_input_widget.text().strip()
        expiry_date = self.expiry_date_edit.date().toString(Qt.DateFormat.ISODate)
        description = self.description_input_widget.text().strip()

        if not name or not price_text or not stock_text:
            self.show_message("Input Error", "Medicine Name, Price, and Stock are required.")
            return

        try:
            price = float(price_text)
            stock = int(stock_text)
            low_stock_alert = int(low_stock_alert_text) if low_stock_alert_text else 10
        except ValueError:
            self.show_message("Input Error", "Price, Stock, and Low Stock Alert must be valid numbers.")
            return

        new_medicine = Medicine(
            name=name, brand=brand, category=category, price=price, stock=stock,
            low_stock_alert=low_stock_alert, expiry_date=expiry_date, description=description
        )

        if self.db_manager.add_medicine(new_medicine):
            self.show_message("Success", f"Medicine '{name}' added successfully.")
            self.load_medicines()
            self.data_changed.emit()  # Emit signal after data change
        # Error messages are handled by DBManager

    def update_medicine(self):
        if self.selected_medicine_id is None:
            self.show_message("Selection Error", "Please select a medicine from the table to update.")
            return

        name = self.name_input_widget.text().strip()
        brand = self.brand_input_widget.text().strip()
        category = self.category_input_widget.text().strip()
        price_text = self.price_input_widget.text().strip()
        stock_text = self.stock_input_widget.text().strip()
        low_stock_alert_text = self.low_stock_alert_input_widget.text().strip()
        expiry_date = self.expiry_date_edit.date().toString(Qt.DateFormat.ISODate)
        description = self.description_input_widget.text().strip()

        if not name or not price_text or not stock_text:
            self.show_message("Input Error", "Medicine Name, Price, and Stock are required.")
            return

        try:
            price = float(price_text)
            stock = int(stock_text)
            low_stock_alert = int(low_stock_alert_text) if low_stock_alert_text else 10
        except ValueError:
            self.show_message("Input Error", "Price, Stock, and Low Stock Alert must be valid numbers.")
            return

        updated_medicine = Medicine(
            medicine_id=self.selected_medicine_id,
            name=name, brand=brand, category=category, price=price, stock=stock,
            low_stock_alert=low_stock_alert, expiry_date=expiry_date, description=description
        )

        if self.db_manager.update_medicine(updated_medicine):
            self.show_message("Success", f"Medicine '{name}' updated successfully.")
            self.load_medicines()
            self.data_changed.emit()  # Emit signal after data change
        # Error messages are handled by DBManager

    def delete_medicine(self):
        if self.selected_medicine_id is None:
            self.show_message("Selection Error", "Please select a medicine from the table to delete.")
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Deletion")
        msg_box.setText(f"Are you sure you want to delete medicine ID {self.selected_medicine_id}?")
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
            if self.db_manager.delete_medicine(self.selected_medicine_id):
                self.show_message("Success", f"Medicine ID {self.selected_medicine_id} deleted successfully.")
                self.load_medicines()
                self.data_changed.emit()  # Emit signal after data change
            # Error messages are handled by DBManager
        else:
            self.show_message("Cancelled", "Deletion cancelled.")

    def load_selected_medicine_to_form(self):
        selected_rows = self.medicine_table.selectedItems()
        if not selected_rows:
            self.clear_form()
            self.selected_medicine_id = None
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.add_button.setEnabled(True)
            return

        row = selected_rows[0].row()
        self.selected_medicine_id = int(self.medicine_table.item(row, 0).text())

        self.name_input_widget.setText(self.medicine_table.item(row, 1).text())
        self.brand_input_widget.setText(self.medicine_table.item(row, 2).text())
        self.category_input_widget.setText(self.medicine_table.item(row, 3).text())
        self.price_input_widget.setText(self.medicine_table.item(row, 4).text())
        self.stock_input_widget.setText(self.medicine_table.item(row, 5).text())
        self.low_stock_alert_input_widget.setText(self.medicine_table.item(row, 6).text())

        expiry_date_str = self.medicine_table.item(row, 7).text()
        if expiry_date_str:
            self.expiry_date_edit.setDate(QDate.fromString(expiry_date_str, Qt.DateFormat.ISODate))
        else:
            self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))

        self.description_input_widget.setText(self.medicine_table.item(row, 8).text())

        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.add_button.setEnabled(False)

    def clear_form(self):
        self.name_input_widget.clear()
        self.brand_input_widget.clear()
        self.category_input_widget.clear()
        self.price_input_widget.clear()
        self.stock_input_widget.clear()
        self.low_stock_alert_input_widget.setText("10")
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        self.description_input_widget.clear()
        self.selected_medicine_id = None
        self.medicine_table.clearSelection()

        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def search_medicines(self):
        search_text = self.search_input.text().strip().lower()
        for row in range(self.medicine_table.rowCount()):
            name_match = search_text in self.medicine_table.item(row, 1).text().lower()
            brand_match = search_text in self.medicine_table.item(row, 2).text().lower()
            category_match = search_text in self.medicine_table.item(row, 3).text().lower()
            self.medicine_table.setRowHidden(row, not (name_match or brand_match or category_match))

    def apply_filter(self):
        filter_type = self.filter_combo.currentText()
        all_medicines = self.db_manager.get_all_medicines() if self.db_manager else []

        for row_idx in range(self.medicine_table.rowCount()):
            self.medicine_table.setRowHidden(row_idx, False)

        if filter_type == "Low Stock":
            for row_idx in range(self.medicine_table.rowCount()):
                stock = int(self.medicine_table.item(row_idx, 5).text())
                low_alert = int(self.medicine_table.item(row_idx, 6).text())
                if stock > low_alert:
                    self.medicine_table.setRowHidden(row_idx, True)
        elif filter_type == "Expired / Expiring Soon":
            today = QDate.currentDate()
            for row_idx in range(self.medicine_table.rowCount()):
                expiry_date_str = self.medicine_table.item(row_idx, 7).text()
                if expiry_date_str:
                    expiry_date = QDate.fromString(expiry_date_str, Qt.DateFormat.ISODate)
                    if expiry_date >= today.addDays(30) or expiry_date < today:
                        self.medicine_table.setRowHidden(row_idx, True)
                else:
                    self.medicine_table.setRowHidden(row_idx, True)

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(
            QMessageBox.Icon.Information if "Success" in title or "Cancelled" in title else QMessageBox.Icon.Warning)
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
    from models.medicine import Medicine
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    db_manager = DBManager("test_pharmacy_medicine.db")

    db_manager.add_medicine(
        Medicine("Paracetamol 500mg", "Tylenol", "Pain Relief", 5.50, 100, expiry_date="2025-12-31"))
    db_manager.add_medicine(
        Medicine("Amoxicillin 250mg", "Amoxil", "Antibiotic", 12.75, 50, low_stock_alert=5, expiry_date="2024-10-15"))
    db_manager.add_medicine(
        Medicine("Vitamin C 1000mg", "Nature's Bounty", "Supplement", 8.99, 20, expiry_date="2026-06-01"))
    db_manager.add_medicine(
        Medicine("Ibuprofen 200mg", "Advil", "Pain Relief", 7.25, 10, low_stock_alert=15, expiry_date="2023-09-01"))
    db_manager.add_medicine(
        Medicine("Cough Syrup", "Robitussin", "Cold & Flu", 9.50, 3, low_stock_alert=5, expiry_date="2024-08-10"))

    medicine_screen = MedicineScreen()
    medicine_screen.set_db_manager(db_manager)
    medicine_screen.showMaximized()
    sys.exit(app.exec())
