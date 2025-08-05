# ui/billing_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
    QSizePolicy, QComboBox, QSpinBox, QApplication, QCompleter
)
from PyQt6.QtGui import QFont, QDoubleValidator # Import QDoubleValidator for numeric input
from PyQt6.QtCore import Qt, QStringListModel, pyqtSignal
import json
from datetime import datetime # Import datetime for invoice date


class BillingScreen(QWidget):
    # Define a signal that will be emitted when a sale is successfully processed
    sale_processed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.cart_items = []
        self.selected_customer = None
        self.setup_ui()
        # Initialize discount and tax values
        self.discount_percentage = 0.0
        self.tax_percentage = 0.0

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Billing System")
        header_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

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

        medicine_selection_layout = QVBoxLayout()
        medicine_selection_layout.addWidget(QLabel("Select Medicine:"))
        self.medicine_search_input = QLineEdit(self)
        self.medicine_search_input.setPlaceholderText("Search medicine by name...")
        self.medicine_search_input.textChanged.connect(self.search_medicines_for_billing)
        medicine_selection_layout.addWidget(self.medicine_search_input)

        self.available_medicines_table = QTableWidget(self)
        self.available_medicines_table.setColumnCount(4)
        self.available_medicines_table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Stock"])
        self.available_medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.available_medicines_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.available_medicines_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        medicine_selection_layout.addWidget(self.available_medicines_table)

        add_to_cart_layout = QHBoxLayout()
        add_to_cart_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spinbox = QSpinBox(self)
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setMaximum(999)
        add_to_cart_layout.addWidget(self.quantity_spinbox)
        self.add_to_cart_button = self._create_button("Add to Cart", "#007bff", font_size=13, padding="8px 15px")
        self.add_to_cart_button.clicked.connect(self.add_selected_medicine_to_cart)
        add_to_cart_layout.addWidget(self.add_to_cart_button)
        medicine_selection_layout.addLayout(add_to_cart_layout)

        top_layout.addLayout(medicine_selection_layout)

        customer_selection_layout = QVBoxLayout()
        customer_selection_layout.addWidget(QLabel("Select Customer (Optional):"))
        self.customer_search_input = QLineEdit(self)
        self.customer_search_input.setPlaceholderText("Search customer by name or phone...")
        self.customer_search_input.textChanged.connect(self.search_customers_for_billing)
        customer_selection_layout.addWidget(self.customer_search_input)

        self.available_customers_table = QTableWidget(self)
        self.available_customers_table.setColumnCount(3)
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
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(25, 25, 25, 25)
        cart_layout.setSpacing(10)

        cart_label = QLabel("Shopping Cart")
        cart_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        cart_layout.addWidget(cart_label)

        self.cart_table = QTableWidget(self)
        self.cart_table.setColumnCount(5)
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

        # --- Subtotal, Discount, Tax, and Grand Total ---
        cart_layout.addSpacing(15) # Add spacing before totals

        # Subtotal
        subtotal_layout = QHBoxLayout()
        subtotal_layout.addStretch()
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.subtotal_amount_label = QLabel("0.00")
        self.subtotal_amount_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        subtotal_layout.addWidget(subtotal_label)
        subtotal_layout.addWidget(self.subtotal_amount_label)
        cart_layout.addLayout(subtotal_layout)

        # Discount Input
        discount_layout = QHBoxLayout()
        discount_layout.addStretch()
        discount_label = QLabel("Discount (%):")
        discount_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.discount_input = QLineEdit(self)
        self.discount_input.setFixedWidth(80)
        self.discount_input.setValidator(QDoubleValidator(0.0, 100.0, 2)) # 0-100%
        self.discount_input.setText("0.00")
        self.discount_input.textChanged.connect(self.calculate_total_amount)
        self.discount_amount_label = QLabel("0.00") # To show calculated discount amount
        self.discount_amount_label.setFont(QFont("Arial", 14))
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        discount_layout.addWidget(QLabel("(-)")) # Indicator for deduction
        discount_layout.addWidget(self.discount_amount_label)
        cart_layout.addLayout(discount_layout)

        # Tax Input
        tax_layout = QHBoxLayout()
        tax_layout.addStretch()
        tax_label = QLabel("Tax (%):")
        tax_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.tax_input = QLineEdit(self)
        self.tax_input.setFixedWidth(80)
        self.tax_input.setValidator(QDoubleValidator(0.0, 100.0, 2)) # 0-100%
        self.tax_input.setText("0.00")
        self.tax_input.textChanged.connect(self.calculate_total_amount)
        self.tax_amount_label = QLabel("0.00") # To show calculated tax amount
        self.tax_amount_label.setFont(QFont("Arial", 14))
        tax_layout.addWidget(tax_label)
        tax_layout.addWidget(self.tax_input)
        tax_layout.addWidget(QLabel("(+)")) # Indicator for addition
        tax_layout.addWidget(self.tax_amount_label)
        cart_layout.addLayout(tax_layout)

        # Grand Total
        grand_total_layout = QHBoxLayout()
        grand_total_layout.addStretch()
        grand_total_label = QLabel("Grand Total:")
        grand_total_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.grand_total_amount_label = QLabel("0.00")
        self.grand_total_amount_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.grand_total_amount_label.setStyleSheet("color: #28a745;") # Green for grand total
        grand_total_layout.addWidget(grand_total_label)
        grand_total_layout.addWidget(self.grand_total_amount_label)
        cart_layout.addLayout(grand_total_layout)

        # --- NEW: Process Sale and Print Invoice Buttons ---
        process_print_buttons_layout = QHBoxLayout()
        process_print_buttons_layout.addStretch() # Push buttons to the right

        self.process_sale_button = self._create_button("Process Sale", "#28a745")
        self.process_sale_button.clicked.connect(self.process_sale)
        process_print_buttons_layout.addWidget(self.process_sale_button)

        self.print_invoice_button = self._create_button("🖨️ Print Invoice", "#17a2b8") # A new button
        self.print_invoice_button.clicked.connect(self._print_invoice)
        process_print_buttons_layout.addWidget(self.print_invoice_button)

        cart_layout.addLayout(process_print_buttons_layout)


        main_layout.addWidget(cart_frame)

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

        # Initial calculation when UI is set up
        self.calculate_total_amount()


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
        self.calculate_total_amount() # Ensure totals are calculated on DB load

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
        self.calculate_total_amount() # Recalculate all totals
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
        self.calculate_total_amount() # Recalculate all totals

    def clear_cart(self):
        """Clears all items from the shopping cart."""
        self.cart_items = []
        self.update_cart_display()
        self.calculate_total_amount() # Recalculate all totals
        self.show_message("Cart Cleared", "Shopping cart has been cleared.")

    def calculate_total_amount(self):
        """Calculates and displays the subtotal, discount, tax, and grand total."""
        subtotal = sum(item["subtotal"] for item in self.cart_items)
        self.subtotal_amount_label.setText(f"{subtotal:.2f}")

        # Get discount and tax percentages from input fields
        try:
            self.discount_percentage = float(self.discount_input.text())
        except ValueError:
            self.discount_percentage = 0.0
            self.discount_input.setText("0.00") # Reset to default if invalid

        try:
            self.tax_percentage = float(self.tax_input.text())
        except ValueError:
            self.tax_percentage = 0.0
            self.tax_input.setText("0.00") # Reset to default if invalid

        # Calculate discount amount
        discount_amount = subtotal * (self.discount_percentage / 100.0)
        self.discount_amount_label.setText(f"{discount_amount:.2f}")

        # Calculate amount after discount
        amount_after_discount = subtotal - discount_amount

        # Calculate tax amount
        tax_amount = amount_after_discount * (self.tax_percentage / 100.0)
        self.tax_amount_label.setText(f"{tax_amount:.2f}")

        # Calculate grand total
        grand_total = amount_after_discount + tax_amount
        self.grand_total_amount_label.setText(f"{grand_total:.2f}")

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

        # Use the grand total from the label
        final_total_amount = float(self.grand_total_amount_label.text())

        customer_id = self.selected_customer.id if self.selected_customer else None
        customer_name = self.selected_customer.name if self.selected_customer else "Walk-in Customer"
        customer_phone = self.selected_customer.phone if self.selected_customer else ""
        customer_email = self.selected_customer.email if self.selected_customer else ""

        # Prepare items for DB: [{"med_id": int, "qty": int, "price": float, "name": str}]
        items_for_db = [
            {"med_id": item["med_id"], "qty": item["qty"], "price": item["price"], "name": item["name"]}
            for item in self.cart_items
        ]

        # In a more advanced system, you might also want to store discount and tax percentages
        # with the sale record in the database. For now, we just pass the final total.

        if self.db_manager.add_sale(customer_id, customer_name, customer_phone, customer_email, final_total_amount,
                                    items_for_db):
            self.show_message("Sale Complete", f"Sale of {final_total_amount:.2f} processed successfully!")
            self.clear_cart()
            self.clear_customer_selection()
            self.load_available_medicines()
            self.load_sales_history()
            self.sale_processed.emit() # Emit signal after successful sale
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

            items_text = ", ".join([f"{item['name']} (x{item['qty']})" for item in sale["items"]])
            self.sales_history_table.setItem(row_idx, 4, QTableWidgetItem(items_text))

        self.sales_history_table.resizeColumnsToContents()
        self.sales_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _generate_invoice_content(self):
        """Generates the detailed invoice content as a formatted string."""
        if not self.cart_items:
            return "No items in cart to generate an invoice."

        # Pharmacy Details (Placeholder - replace with actual details)
        invoice_content = "--- PharmaCare Invoice ---\n"
        invoice_content += "Pharmacy Name: PharmaCare\n"
        invoice_content += "Address: 123 Health St, Wellness City\n"
        invoice_content += "Contact: +92 3XX XXXXXXX | info@pharmacare.com\n"
        invoice_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        invoice_content += "--------------------------\n\n"

        # Customer Details
        if self.selected_customer:
            invoice_content += f"Customer: {self.selected_customer.name}\n"
            if self.selected_customer.phone:
                invoice_content += f"Phone: {self.selected_customer.phone}\n"
            if self.selected_customer.email:
                invoice_content += f"Email: {self.selected_customer.email}\n"
            invoice_content += "\n"
        else:
            invoice_content += "Customer: Walk-in Customer\n\n"

        # Items Sold
        invoice_content += "{:<25} {:>10} {:>8} {:>12}\n".format("Medicine", "Price", "Qty", "Subtotal")
        invoice_content += "-" * 60 + "\n"
        for item in self.cart_items:
            invoice_content += "{:<25} {:>10.2f} {:>8} {:>12.2f}\n".format(
                item["name"], item["price"], item["qty"], item["subtotal"]
            )
        invoice_content += "-" * 60 + "\n"

        # Summary of Charges
        subtotal = sum(item["subtotal"] for item in self.cart_items)
        discount_amount = subtotal * (self.discount_percentage / 100.0)
        amount_after_discount = subtotal - discount_amount
        tax_amount = amount_after_discount * (self.tax_percentage / 100.0)
        grand_total = amount_after_discount + tax_amount

        invoice_content += f"Subtotal: {'':<35} {subtotal:>10.2f}\n"
        invoice_content += f"Discount ({self.discount_percentage:.2f}%): {'':<28} -{discount_amount:>10.2f}\n"
        invoice_content += f"Tax ({self.tax_percentage:.2f}%): {'':<33} +{tax_amount:>10.2f}\n"
        invoice_content += f"Grand Total: {'':<34} {grand_total:>10.2f}\n"
        invoice_content += "--------------------------\n"
        invoice_content += "Thank you for your purchase!\n"
        invoice_content += "--------------------------"

        return invoice_content

    def _print_invoice(self):
        """Displays the generated invoice content in a message box."""
        invoice_text = self._generate_invoice_content()
        self.show_message("Printable Invoice", invoice_text)
        # For actual printing, you would use QPrintDialog and QPrinter here.
        # Example (conceptual, requires more setup):
        # printer = QPrinter()
        # print_dialog = QPrintDialog(printer, self)
        # if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
        #     document = QTextDocument()
        #     document.setPlainText(invoice_text)
        #     document.print(printer)

    def show_message(self, title, message):
        """Displays an information or error message box."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(
            QMessageBox.Icon.Information if "Success" in title or "Complete" in title or "Invoice" in title else QMessageBox.Icon.Warning)
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
    from datetime import datetime, timedelta

    app = QApplication(sys.argv)
    db_manager = DBManager("test_pharmacy_billing.db")

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
    billing_screen.set_db_manager(db_manager)
    billing_screen.showMaximized()
    sys.exit(app.exec())
