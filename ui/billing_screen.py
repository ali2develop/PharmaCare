# ui/billing_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
    QSizePolicy, QComboBox, QSpinBox, QApplication, QCompleter
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QStringListModel
from models.medicine import Medicine
from models.customer import Customer
import json


class BillingScreen(QWidget):
    """
    UI for managing sales and billing. Allows selecting medicines and customers,
    adding items to a cart, calculating total, and processing sales.
    """

    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.cart_items = []
        self.selected_customer = None
        self.setup_ui()

    def setup_ui(self):
        """Sets up the layout and widgets for the billing screen."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Header Section ---
        header_label = QLabel("Billing System")
        header_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        # --- Top Section: Customer & Medicine Selection ---
        top_frame = QFrame(self)
        top_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #007bff;
            }
            QTableWidget {
                background-color: #f8f8f8;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #e0e2e5;
                padding: 5px;
                border: 1px solid #d0d2d5;
                font-weight: bold;
                color: #34495e;
            }
        """)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(25, 25, 25, 25)
        top_layout.setSpacing(20)

        # Left Side: Medicine Search & Add to Cart
        medicine_selection_layout = QVBoxLayout()
        medicine_selection_layout.addWidget(QLabel("Select Medicine:"))
        self.medicine_search_input = QLineEdit(self)
        self.medicine_search_input.setPlaceholderText("Search medicine by name...")
        self.medicine_search_input.textChanged.connect(self.search_medicines_for_billing)
        medicine_selection_layout.addWidget(self.medicine_search_input)

        self.available_medicines_table = QTableWidget(self)
        self.available_medicines_table.setColumnCount(4)  # ID, Name, Price, Stock
        self.available_medicines_table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Stock"])
        self.available_medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.available_medicines_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.available_medicines_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        medicine_selection_layout.addWidget(self.available_medicines_table)

        add_to_cart_layout = QHBoxLayout()
        add_to_cart_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spinbox = QSpinBox(self)
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setMaximum(999)  # Max reasonable quantity
        add_to_cart_layout.addWidget(self.quantity_spinbox)
        self.add_to_cart_button = self._create_button("Add to Cart", "#007bff", font_size=13, padding="8px 15px")
        self.add_to_cart_button.clicked.connect(self.add_selected_medicine_to_cart)
        add_to_cart_layout.addWidget(self.add_to_cart_button)
        medicine_selection_layout.addLayout(add_to_cart_layout)

        top_layout.addLayout(medicine_selection_layout)

        # Right Side: Customer Selection
        customer_selection_layout = QVBoxLayout()
        customer_selection_layout.addWidget(QLabel("Select Customer (Optional):"))
        self.customer_search_input = QLineEdit(self)
        self.customer_search_input.setPlaceholderText("Search customer by name or phone...")
        self.customer_search_input.textChanged.connect(self.search_customers_for_billing)
        customer_selection_layout.addWidget(self.customer_search_input)

        self.available_customers_table = QTableWidget(self)
        self.available_customers_table.setColumnCount(3)  # ID, Name, Phone
        self.available_customers_table.setHorizontalHeaderLabels(["ID", "Name", "Phone"])
        self.available_customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.available_customers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.available_customers_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.available_customers_table.itemSelectionChanged.connect(self.customer_selected)
        customer_selection_layout.addWidget(self.available_customers_table)

        self.clear_customer_button = self._create_button("Clear Customer", "#6c757d", font_size=13, padding="8px 15px")
        self.clear_customer_button.clicked.connect(self.clear_customer_selection)
        customer_selection_layout.addWidget(self.clear_customer_button)

        top_layout.addLayout(customer_selection_layout)

        main_layout.addWidget(top_frame)

        # --- Middle Section: Cart & Totals ---
        cart_frame = QFrame(self)
        cart_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget {
                background-color: #f8f8f8;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #e0e2e5;
                padding: 8px;
                border: 1px solid #d0d2d5;
                font-weight: bold;
                color: #34495e;
            }
        """)
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(25, 25, 25, 25)
        cart_layout.setSpacing(10)

        cart_label = QLabel("Shopping Cart")
        cart_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        cart_layout.addWidget(cart_label)

        self.cart_table = QTableWidget(self)
        self.cart_table.setColumnCount(5)  # ID, Name, Price, Quantity, Subtotal
        self.cart_table.setHorizontalHeaderLabels(["ID", "Medicine", "Price", "Qty", "Subtotal"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cart_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        cart_layout.addWidget(self.cart_table)

        cart_buttons_layout = QHBoxLayout()
        self.remove_item_button = self._create_button("Remove Item", "#dc3545", font_size=13, padding="8px 15px")
        self.remove_item_button.clicked.connect(self.remove_selected_cart_item)
        self.clear_cart_button = self._create_button("Clear Cart", "#ffc107", font_size=13, padding="8px 15px")
        self.clear_cart_button.clicked.connect(self.clear_cart)
        cart_buttons_layout.addStretch()
        cart_buttons_layout.addWidget(self.remove_item_button)
        cart_buttons_layout.addWidget(self.clear_cart_button)
        cart_buttons_layout.addStretch()
        cart_layout.addLayout(cart_buttons_layout)

        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_label = QLabel("Total Amount:")
        total_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.total_amount_label = QLabel("0.00")
        self.total_amount_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.total_amount_label.setStyleSheet("color: #28a745;")
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_amount_label)
        cart_layout.addLayout(total_layout)

        self.process_sale_button = self._create_button("Process Sale", "#28a745")
        self.process_sale_button.clicked.connect(self.process_sale)
        cart_layout.addWidget(self.process_sale_button)

        main_layout.addWidget(cart_frame)

        # --- Bottom Section: Recent Sales History ---
        sales_history_frame = QFrame(self)
        sales_history_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget {
                background-color: #f8f8f8;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #e0e2e5;
                padding: 5px;
                border: 1px solid #d0d2d5;
                font-weight: bold;
                color: #34495e;
            }
        """)
        sales_history_layout = QVBoxLayout(sales_history_frame)
        sales_history_layout.setContentsMargins(25, 25, 25, 25)
        sales_history_layout.setSpacing(10)

        sales_history_label = QLabel("Recent Sales History")
        sales_history_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        sales_history_layout.addWidget(sales_history_label)

        self.sales_history_table = QTableWidget(self)
        self.sales_history_table.setColumnCount(5)
        self.sales_history_table.setHorizontalHeaderLabels(
            ["Sale ID", "Customer", "Total Amount", "Date", "Items Sold"])
        self.sales_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sales_history_layout.addWidget(self.sales_history_table)

        main_layout.addWidget(sales_history_frame)

        self.setStyleSheet("background-color: #f0f2f5;")

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
        """Sets the DBManager instance for this screen and loads initial data."""
        self.db_manager = db_manager
        self.load_available_medicines()
        self.load_available_customers()
        self.load_sales_history()

    def load_available_medicines(self):
        """Loads all medicines from the database into the available medicines table."""
        if not self.db_manager: return
        medicines = self.db_manager.get_all_medicines()
        self.available_medicines_table.setRowCount(len(medicines))
        for row_idx, med in enumerate(medicines):
            self.available_medicines_table.setItem(row_idx, 0, QTableWidgetItem(str(med.id)))
            self.available_medicines_table.setItem(row_idx, 1, QTableWidgetItem(med.name))
            self.available_medicines_table.setItem(row_idx, 2, QTableWidgetItem(f"{med.price:.2f}"))
            self.available_medicines_table.setItem(row_idx, 3, QTableWidgetItem(str(med.stock)))
        self.available_medicines_table.resizeColumnsToContents()
        self.available_medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def search_medicines_for_billing(self):
        """Filters available medicines table based on search input."""
        search_text = self.medicine_search_input.text().strip().lower()
        for row in range(self.available_medicines_table.rowCount()):
            name_match = search_text in self.available_medicines_table.item(row, 1).text().lower()
            self.available_medicines_table.setRowHidden(row, not name_match)

    def add_selected_medicine_to_cart(self):
        """Adds the selected medicine from the available medicines table to the cart."""
        selected_rows = self.available_medicines_table.selectedItems()
        if not selected_rows:
            self.show_message("Selection Error", "Please select a medicine from the list to add to cart.")
            return

        row = selected_rows[0].row()
        med_id = int(self.available_medicines_table.item(row, 0).text())
        med_name = self.available_medicines_table.item(row, 1).text()
        med_price = float(self.available_medicines_table.item(row, 2).text())
        available_stock = int(self.available_medicines_table.item(row, 3).text())
        quantity = self.quantity_spinbox.value()

        if quantity <= 0:
            self.show_message("Input Error", "Quantity must be greater than zero.")
            return
        if quantity > available_stock:
            self.show_message("Stock Error", f"Only {available_stock} of {med_name} available in stock.")
            return

        # Check if item already in cart, update quantity
        found_in_cart = False
        for item in self.cart_items:
            if item["med_id"] == med_id:
                new_qty = item["qty"] + quantity
                if new_qty > available_stock:
                    self.show_message("Stock Error",
                                      f"Adding {quantity} more would exceed available stock of {available_stock} for {med_name}.")
                    return
                item["qty"] = new_qty
                item["subtotal"] = item["qty"] * item["price"]
                found_in_cart = True
                break

        if not found_in_cart:
            # Add new item to cart
            subtotal = med_price * quantity
            self.cart_items.append({
                "med_id": med_id,
                "name": med_name,
                "price": med_price,
                "qty": quantity,
                "subtotal": subtotal
            })

        self.update_cart_display()
        self.calculate_total_amount()
        self.available_medicines_table.clearSelection()

    def update_cart_display(self):
        """Refreshes the cart table with current cart items."""
        self.cart_table.setRowCount(len(self.cart_items))
        for row_idx, item in enumerate(self.cart_items):
            self.cart_table.setItem(row_idx, 0, QTableWidgetItem(str(item["med_id"])))
            self.cart_table.setItem(row_idx, 1, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(row_idx, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(row_idx, 3, QTableWidgetItem(str(item["qty"])))
            self.cart_table.setItem(row_idx, 4, QTableWidgetItem(f"{item['subtotal']:.2f}"))
        self.cart_table.resizeColumnsToContents()
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def remove_selected_cart_item(self):
        """Removes the selected item from the cart."""
        selected_rows = self.cart_table.selectedItems()
        if not selected_rows:
            self.show_message("Selection Error", "Please select an item in the cart to remove.")
            return

        row_idx = selected_rows[0].row()
        del self.cart_items[row_idx]
        self.update_cart_display()
        self.calculate_total_amount()

    def clear_cart(self):
        """Clears all items from the shopping cart."""
        self.cart_items = []
        self.update_cart_display()
        self.calculate_total_amount()
        self.show_message("Cart Cleared", "Shopping cart has been cleared.")

    def calculate_total_amount(self):
        """Calculates and displays the total amount of items in the cart."""
        total = sum(item["subtotal"] for item in self.cart_items)
        self.total_amount_label.setText(f"{total:.2f}")

    def load_available_customers(self):
        """Loads all customers from the database into the available customers table."""
        if not self.db_manager: return
        customers = self.db_manager.get_all_customers()
        self.available_customers_table.setRowCount(len(customers))
        for row_idx, cust in enumerate(customers):
            self.available_customers_table.setItem(row_idx, 0, QTableWidgetItem(str(cust.id)))
            self.available_customers_table.setItem(row_idx, 1, QTableWidgetItem(cust.name))
            self.available_customers_table.setItem(row_idx, 2, QTableWidgetItem(cust.phone if cust.phone else ""))
        self.available_customers_table.resizeColumnsToContents()
        self.available_customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def search_customers_for_billing(self):
        """Filters available customers table based on search input."""
        search_text = self.customer_search_input.text().strip().lower()
        for row in range(self.available_customers_table.rowCount()):
            name_match = search_text in self.available_customers_table.item(row, 1).text().lower()
            phone_match = search_text in self.available_customers_table.item(row, 2).text().lower()
            self.available_customers_table.setRowHidden(row, not (name_match or phone_match))

    def customer_selected(self):
        """Sets the selected customer based on table selection."""
        selected_rows = self.available_customers_table.selectedItems()
        if not selected_rows:
            self.selected_customer = None
            return

        row = selected_rows[0].row()
        customer_id = int(self.available_customers_table.item(row, 0).text())
        # Retrieve full customer object from DB for complete details
        self.selected_customer = self.db_manager.get_customer_by_id(customer_id)
        if self.selected_customer:
            self.show_message("Customer Selected", f"Customer '{self.selected_customer.name}' selected for this sale.")
        else:
            self.show_message("Error", "Could not retrieve selected customer details.")
            self.clear_customer_selection()  # Clear selection if retrieval fails

    def clear_customer_selection(self):
        """Clears the selected customer."""
        self.selected_customer = None
        self.available_customers_table.clearSelection()
        self.customer_search_input.clear()
        self.show_message("Customer Cleared", "Customer selection has been cleared.")

    def process_sale(self):
        """Processes the sale, records it in the database, and updates stock."""
        if not self.cart_items:
            self.show_message("Sale Error", "The cart is empty. Please add medicines to proceed.")
            return

        total_amount = float(self.total_amount_label.text())

        customer_id = self.selected_customer.id if self.selected_customer else None
        customer_name = self.selected_customer.name if self.selected_customer else "Walk-in Customer"
        customer_phone = self.selected_customer.phone if self.selected_customer else ""
        customer_email = self.selected_customer.email if self.selected_customer else ""

        # Prepare items for DB: [{"med_id": int, "qty": int, "price": float, "name": str}]
        # Ensure 'name' is included for sales history readability
        items_for_db = [
            {"med_id": item["med_id"], "qty": item["qty"], "price": item["price"], "name": item["name"]}
            for item in self.cart_items
        ]

        if self.db_manager.add_sale(customer_id, customer_name, customer_phone, customer_email, total_amount,
                                    items_for_db):
            self.show_message("Sale Complete", f"Sale of {total_amount:.2f} processed successfully!")
            self.clear_cart()  # Clear cart after successful sale
            self.clear_customer_selection()  # Clear customer after successful sale
            self.load_available_medicines()  # Refresh medicine stock display
            self.load_sales_history()  # Refresh sales history
        # Error messages handled by DBManager's add_sale method

    def load_sales_history(self):
        """Loads recent sales from the database into the sales history table."""
        if not self.db_manager: return
        sales = self.db_manager.get_all_sales()
        self.sales_history_table.setRowCount(len(sales))

        for row_idx, sale in enumerate(sales):
            self.sales_history_table.setItem(row_idx, 0, QTableWidgetItem(str(sale["id"])))
            self.sales_history_table.setItem(row_idx, 1, QTableWidgetItem(sale["customer_name"]))
            self.sales_history_table.setItem(row_idx, 2, QTableWidgetItem(f"{sale['total_amount']:.2f}"))
            self.sales_history_table.setItem(row_idx, 3, QTableWidgetItem(sale["sale_date"]))

            # Display items in a readable format
            items_text = ", ".join([f"{item['name']} (x{item['qty']})" for item in sale["items"]])
            self.sales_history_table.setItem(row_idx, 4, QTableWidgetItem(items_text))

        self.sales_history_table.resizeColumnsToContents()
        self.sales_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def show_message(self, title, message):
        """Displays an information or error message box."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(
            QMessageBox.Icon.Information if "Success" in title or "Complete" in title else QMessageBox.Icon.Warning)
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
    from models.customer import Customer

    app = QApplication(sys.argv)
    db_manager = DBManager("test_pharmacy_billing.db")  # Use a test DB for standalone running

    # Add some dummy data for testing
    db_manager.add_medicine(
        Medicine("Paracetamol 500mg", "Tylenol", "Pain Relief", 5.50, 100, expiry_date="2025-12-31"))
    db_manager.add_medicine(
        Medicine("Amoxicillin 250mg", "Amoxil", "Antibiotic", 12.75, 50, low_stock_alert=5, expiry_date="2024-10-15"))
    db_manager.add_customer(
        Customer(name="John Doe", phone="123-456-7890", email="john.doe@example.com", address="123 Main St"))
    db_manager.add_customer(
        Customer(name="Jane Smith", phone="987-654-3210", email="jane.smith@example.com", address="456 Oak Ave"))

    billing_screen = BillingScreen()
    billing_screen.set_db_manager(db_manager)  # Pass the DB manager
    billing_screen.showMaximized()
    sys.exit(app.exec())
