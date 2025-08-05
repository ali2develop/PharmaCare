# ui/reports_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QFrame, QApplication,
    QSizePolicy, QMessageBox # Added QMessageBox for show_message
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate

class ReportsScreen(QWidget):
    """
    UI for generating and viewing various pharmacy reports.
    """
    def __init__(self):
        super().__init__()
        self.db_manager = None # Will be set by DashboardScreen
        self.setup_ui()

    def setup_ui(self):
        """Sets up the layout and widgets for the reports screen."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Header Section ---
        header_label = QLabel("Reports & Analytics")
        header_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        # --- Report Controls Frame ---
        controls_frame = QFrame(self)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
            }
            QComboBox, QDateEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QComboBox:focus, QDateEdit:focus {
                border: 2px solid #007bff;
            }
            QPushButton {
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(25, 15, 25, 15)
        controls_layout.setSpacing(10)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        controls_layout.addWidget(QLabel("Report Type:"))
        self.report_type_combo = QComboBox(self)
        self.report_type_combo.addItem("Sales by Date Range")
        self.report_type_combo.addItem("Current Stock Overview")
        self.report_type_combo.addItem("Low Stock Medicines")
        self.report_type_combo.addItem("Expiring Medicines")
        self.report_type_combo.currentIndexChanged.connect(self.update_date_inputs_visibility)
        controls_layout.addWidget(self.report_type_combo)

        # Store references to these labels
        self.from_label = QLabel("From:")
        controls_layout.addWidget(self.from_label)
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1)) # Default to last month
        controls_layout.addWidget(self.start_date_edit)

        self.to_label = QLabel("To:")
        controls_layout.addWidget(self.to_label)
        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate()) # Default to today
        controls_layout.addWidget(self.end_date_edit)

        self.generate_report_button = self._create_button("Generate Report", "#007bff")
        self.generate_report_button.clicked.connect(self.generate_report)
        controls_layout.addWidget(self.generate_report_button)

        controls_layout.addStretch() # Push controls to the left

        main_layout.addWidget(controls_frame)

        # --- Report Display Table ---
        self.report_table = QTableWidget(self)
        self.report_table.setColumnCount(0) # Will be set dynamically
        self.report_table.setHorizontalHeaderLabels([]) # Will be set dynamically
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.report_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection) # Reports are usually read-only
        self.report_table.setStyleSheet("""
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
        """)
        main_layout.addWidget(self.report_table)

        main_layout.addStretch() # Push content to the top

        self.setStyleSheet("background-color: #f0f2f5;")
        self.update_date_inputs_visibility() # Set initial visibility

    def _create_button(self, text, color, font_size=14, padding="12px 25px"):
        """Helper to create a styled QPushButton."""
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
        """Helper to darken a hex color."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}"

    def set_db_manager(self, db_manager):
        """Sets the DBManager instance for this screen."""
        self.db_manager = db_manager
        # Automatically generate a default report when screen is loaded
        self.generate_report()

    def update_date_inputs_visibility(self):
        """Hides/shows date inputs based on selected report type."""
        report_type = self.report_type_combo.currentText()
        is_date_range_report = (report_type == "Sales by Date Range")
        self.start_date_edit.setVisible(is_date_range_report)
        self.end_date_edit.setVisible(is_date_range_report)
        self.from_label.setVisible(is_date_range_report) # Use stored reference
        self.to_label.setVisible(is_date_range_report)   # Use stored reference

    def generate_report(self):
        """Generates the selected report and displays it in the table."""
        if not self.db_manager:
            self.show_message("Error", "Database manager not set.")
            return

        report_type = self.report_type_combo.currentText()
        self.report_table.setRowCount(0) # Clear previous results

        if report_type == "Sales by Date Range":
            start_date = self.start_date_edit.date().toString(Qt.DateFormat.ISODate)
            end_date = self.end_date_edit.date().toString(Qt.DateFormat.ISODate)
            self._generate_sales_report(start_date, end_date)
        elif report_type == "Current Stock Overview":
            self._generate_current_stock_report()
        elif report_type == "Low Stock Medicines":
            self._generate_low_stock_report()
        elif report_type == "Expiring Medicines":
            self._generate_expiring_medicines_report()

    def _generate_sales_report(self, start_date, end_date):
        """Generates and displays a sales report for a given date range."""
        sales = self.db_manager.get_sales_in_date_range(start_date, end_date)
        if not sales:
            self.show_message("No Data", f"No sales found between {start_date} and {end_date}.")
            self.report_table.setColumnCount(0)
            self.report_table.setHorizontalHeaderLabels([])
            return

        headers = ["Sale ID", "Customer Name", "Total Amount (PKR)", "Sale Date", "Items Sold"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(sales))

        for row_idx, sale in enumerate(sales):
            self.report_table.setItem(row_idx, 0, QTableWidgetItem(str(sale["id"])))
            self.report_table.setItem(row_idx, 1, QTableWidgetItem(sale["customer_name"]))
            self.report_table.setItem(row_idx, 2, QTableWidgetItem(f"{sale['total_amount']:.2f}"))
            self.report_table.setItem(row_idx, 3, QTableWidgetItem(sale["sale_date"]))
            items_text = ", ".join([f"{item['name']} (x{item['qty']})" for item in sale["items"]])
            self.report_table.setItem(row_idx, 4, QTableWidgetItem(items_text))
        self.report_table.resizeColumnsToContents()
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _generate_current_stock_report(self):
        """Generates and displays a report of all medicines and their current stock."""
        medicines = self.db_manager.get_all_medicines()
        if not medicines:
            self.show_message("No Data", "No medicines found in inventory.")
            self.report_table.setColumnCount(0)
            self.report_table.setHorizontalHeaderLabels([])
            return

        headers = ["ID", "Medicine Name", "Brand", "Category", "Current Stock", "Price (PKR)", "Expiry Date"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(medicines))

        for row_idx, med in enumerate(medicines):
            self.report_table.setItem(row_idx, 0, QTableWidgetItem(str(med.id)))
            self.report_table.setItem(row_idx, 1, QTableWidgetItem(med.name))
            self.report_table.setItem(row_idx, 2, QTableWidgetItem(med.brand if med.brand else "N/A"))
            self.report_table.setItem(row_idx, 3, QTableWidgetItem(med.category if med.category else "N/A"))
            self.report_table.setItem(row_idx, 4, QTableWidgetItem(str(med.stock)))
            self.report_table.setItem(row_idx, 5, QTableWidgetItem(f"{med.price:.2f}"))
            self.report_table.setItem(row_idx, 6, QTableWidgetItem(med.expiry_date if med.expiry_date else "N/A"))
        self.report_table.resizeColumnsToContents()
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _generate_low_stock_report(self):
        """Generates and displays a report of medicines with low stock."""
        low_stock_medicines = self.db_manager.get_all_low_stock_medicines()
        if not low_stock_medicines:
            self.show_message("No Data", "No medicines currently have low stock.")
            self.report_table.setColumnCount(0)
            self.report_table.setHorizontalHeaderLabels([])
            return

        headers = ["ID", "Medicine Name", "Brand", "Current Stock", "Low Alert Threshold", "Expiry Date"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(low_stock_medicines))

        for row_idx, med in enumerate(low_stock_medicines):
            self.report_table.setItem(row_idx, 0, QTableWidgetItem(str(med.id)))
            self.report_table.setItem(row_idx, 1, QTableWidgetItem(med.name))
            self.report_table.setItem(row_idx, 2, QTableWidgetItem(med.brand if med.brand else "N/A"))
            self.report_table.setItem(row_idx, 3, QTableWidgetItem(str(med.stock)))
            self.report_table.setItem(row_idx, 4, QTableWidgetItem(str(med.low_stock_alert)))
            self.report_table.setItem(row_idx, 5, QTableWidgetItem(med.expiry_date if med.expiry_date else "N/A"))
        self.report_table.resizeColumnsToContents()
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _generate_expiring_medicines_report(self):
        """Generates and displays a report of medicines expiring soon or already expired."""
        expiring_medicines = self.db_manager.get_all_expiring_medicines(days_threshold=90)
        if not expiring_medicines:
            self.show_message("No Data", "No medicines expiring within the next 90 days or already expired.")
            self.report_table.setColumnCount(0)
            self.report_table.setHorizontalHeaderLabels([])
            return

        headers = ["ID", "Medicine Name", "Brand", "Current Stock", "Expiry Date"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(expiring_medicines))

        for row_idx, med in enumerate(expiring_medicines):
            self.report_table.setItem(row_idx, 0, QTableWidgetItem(str(med.id)))
            self.report_table.setItem(row_idx, 1, QTableWidgetItem(med.name))
            self.report_table.setItem(row_idx, 2, QTableWidgetItem(med.brand if med.brand else "N/A"))
            self.report_table.setItem(row_idx, 3, QTableWidgetItem(str(med.stock)))
            self.report_table.setItem(row_idx, 4, QTableWidgetItem(med.expiry_date if med.expiry_date else "N/A"))
        self.report_table.resizeColumnsToContents()
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def show_message(self, title, message):
        """Displays an information or error message box."""
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
    # Import datetime and timedelta for the example usage below
    from datetime import datetime, timedelta
    from database.db_manager import DBManager
    from models.medicine import Medicine
    from models.customer import Customer
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    db_manager = DBManager("test_pharmacy_reports.db") # Use a test DB

    # Add some dummy data for testing reports
    db_manager.add_medicine(
        Medicine("Paracetamol 500mg", "Tylenol", "Pain Relief", 5.50, 100, expiry_date="2025-12-31"))
    db_manager.add_medicine(
        Medicine("Amoxicillin 250mg", "Amoxil", "Antibiotic", 12.75, 50, low_stock_alert=5, expiry_date="2024-10-15"))
    db_manager.add_medicine(Medicine("Expired Med", "Brand X", "Expired", 10.0, 5, expiry_date="2023-01-01"))
    db_manager.add_medicine(Medicine("Low Stock Med", "Brand Y", "Pain", 20.0, 2, low_stock_alert=5, expiry_date="2025-01-01"))
    db_manager.add_medicine(Medicine("Expiring Soon", "Brand Z", "Supplement", 15.0, 10, expiry_date=QDate.currentDate().addDays(10).toString(Qt.DateFormat.ISODate)))

    db_manager.add_customer(Customer(name="John Doe", phone="123-456-7890", email="john.doe@example.com", address="123 Main St"))

    # Add some sales data for reporting
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(weeks=1)

    db_manager.add_sale(1, "John Doe", "123-456-7890", "john.doe@example.com", 11.00, [{"med_id": 1, "qty": 2, "price": 5.50, "name": "Paracetamol 500mg"}])
    db_manager.add_sale(None, "Walk-in", "", "", 12.75, [{"med_id": 2, "qty": 1, "price": 12.75, "name": "Amoxicillin 250mg"}])
    db_manager.add_sale(1, "John Doe", "123-456-7890", "john.doe@example.com", 20.00, [{"med_id": 1, "qty": 1, "price": 5.50, "name": "Paracetamol 500mg"}, {"med_id": 2, "qty": 1, "price": 12.75, "name": "Amoxicillin 250mg"}])


    reports_screen = ReportsScreen()
    reports_screen.set_db_manager(db_manager) # Pass the DB manager
    reports_screen.showMaximized()
    sys.exit(app.exec())
