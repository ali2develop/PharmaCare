# ui/dashboard_content_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QApplication
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class DashboardContentScreen(QWidget):
    """
    The enhanced dashboard content screen, displaying key pharmacy statistics.
    """

    def __init__(self):
        super().__init__()
        self.db_manager = None  # Initialize db_manager
        self.setup_ui()

    def setup_ui(self):
        """Sets up the layout and widgets for the dashboard content screen."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Existing Welcome Label
        welcome_label = QLabel("Welcome to Your PharmaCare Dashboard!", self)
        welcome_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(welcome_label)

        # Existing Info Label
        info_label = QLabel("Use the sidebar to navigate through different sections.", self)
        info_label.setFont(QFont("Arial", 16))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #34495e;")
        main_layout.addWidget(info_label)

        # --- NEW: Statistics Cards Layout ---
        main_layout.addSpacing(40)  # Add some space before the stats

        stats_grid_layout = QHBoxLayout()
        stats_grid_layout.setSpacing(20)
        stats_grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Total Medicines Card
        self.total_medicines_card = self._create_stat_card("Total Medicines", "0", "#3498db")
        stats_grid_layout.addWidget(self.total_medicines_card)

        # Total Customers Card
        self.total_customers_card = self._create_stat_card("Total Customers", "0", "#2ecc71")
        stats_grid_layout.addWidget(self.total_customers_card)

        # Total Sales Amount Card
        self.total_sales_card = self._create_stat_card("Total Sales (PKR)", "0.00", "#f39c12")
        stats_grid_layout.addWidget(self.total_sales_card)

        main_layout.addLayout(stats_grid_layout)

        # --- NEW: Alerts/Important Info Cards Layout ---
        main_layout.addSpacing(20)  # Space between stat rows

        alerts_grid_layout = QHBoxLayout()
        alerts_grid_layout.setSpacing(20)
        alerts_grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Low Stock Medicines Card
        self.low_stock_card = self._create_stat_card("Low Stock Items", "0", "#e74c3c")
        alerts_grid_layout.addWidget(self.low_stock_card)

        # Expiring Medicines Card
        self.expiring_medicines_card = self._create_stat_card("Expiring Soon", "0", "#9b59b6")
        alerts_grid_layout.addWidget(self.expiring_medicines_card)

        main_layout.addLayout(alerts_grid_layout)

        main_layout.addStretch()  # Push content to the top

        self.setStyleSheet("background-color: #f0f2f5;")

    def _create_stat_card(self, title, value, color):
        """Helper to create a styled statistics card."""
        card_frame = QFrame(self)
        card_frame.setFixedSize(220, 150)  # Fixed size for uniformity
        card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }}
            QLabel {{
                color: #34495e;
            }}
            QLabel#value_label {{
                color: {color};
            }}
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title, card_frame)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)

        value_label = QLabel(value, card_frame)
        value_label.setObjectName("value_label")  # Object name for specific styling
        value_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)

        card_frame.value_label = value_label  # Store reference to update later
        return card_frame

    def set_db_manager(self, db_manager):
        """Sets the DBManager instance and loads initial dashboard statistics."""
        self.db_manager = db_manager
        self.load_dashboard_stats()

    def load_dashboard_stats(self):
        """Fetches and displays the latest dashboard statistics."""
        if not self.db_manager:
            print("DBManager not set for DashboardContentScreen.")
            return

        total_medicines = self.db_manager.get_total_medicines()
        total_customers = self.db_manager.get_total_customers()
        total_sales_amount = self.db_manager.get_total_sales_amount()
        low_stock_count = self.db_manager.get_low_stock_medicines_count()
        expiring_count = self.db_manager.get_expiring_medicines_count(days_threshold=30)  # Within 30 days

        self.total_medicines_card.value_label.setText(str(total_medicines))
        self.total_customers_card.value_label.setText(str(total_customers))
        self.total_sales_card.value_label.setText(f"{total_sales_amount:.2f}")
        self.low_stock_card.value_label.setText(str(low_stock_count))
        self.expiring_medicines_card.value_label.setText(str(expiring_count))

        print("Dashboard statistics updated.")


if __name__ == "__main__":
    import sys
    # Import datetime and timedelta for the example usage below
    from datetime import datetime, timedelta
    from database.db_manager import DBManager
    from models.medicine import Medicine
    from models.customer import Customer
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    db_manager = DBManager("test_pharmacy_dashboard_stats.db")  # Use a test DB

    # Add some dummy data for testing dashboard stats
    db_manager.add_medicine(
        Medicine("Paracetamol 500mg", "Tylenol", "Pain Relief", 5.50, 100, expiry_date="2025-12-31"))
    db_manager.add_medicine(
        Medicine("Amoxicillin 250mg", "Amoxil", "Antibiotic", 12.75, 50, low_stock_alert=5, expiry_date="2024-10-15"))
    db_manager.add_medicine(Medicine("Expired Med", "Brand X", "Expired", 10.0, 5, expiry_date="2023-01-01"))  # Expired
    db_manager.add_medicine(
        Medicine("Low Stock Med", "Brand Y", "Pain", 20.0, 2, low_stock_alert=5, expiry_date="2025-01-01"))  # Low stock
    db_manager.add_medicine(Medicine("Expiring Soon", "Brand Z", "Supplement", 15.0, 10,
                                     expiry_date=(datetime.now() + timedelta(days=10)).strftime(
                                         '%Y-%m-%d')))  # Expiring soon

    db_manager.add_customer(
        Customer(name="John Doe", phone="123-456-7890", email="john.doe@example.com", address="123 Main St"))
    db_manager.add_customer(
        Customer(name="Jane Smith", phone="987-654-3210", email="jane.smith@example.com", address="456 Oak Ave"))

    # Add some sales data
    items_sale1 = [{"med_id": 1, "qty": 2, "price": 5.50, "name": "Paracetamol 500mg"}]
    db_manager.add_sale(1, "John Doe", "123-456-7890", "john.doe@example.com", 11.00, items_sale1)
    items_sale2 = [{"med_id": 2, "qty": 1, "price": 12.75, "name": "Amoxicillin 250mg"}]
    db_manager.add_sale(None, "Walk-in", "", "", 12.75, items_sale2)

    dashboard_content_screen = DashboardContentScreen()
    dashboard_content_screen.set_db_manager(db_manager)  # Pass the DB manager
    dashboard_content_screen.showMaximized()
    sys.exit(app.exec())
