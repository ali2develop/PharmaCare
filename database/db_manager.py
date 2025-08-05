# database/db_manager.py

import sqlite3
from PyQt6.QtWidgets import QMessageBox
import bcrypt
import json # Ensure json is imported

# Import models
from models.user import User
from models.medicine import Medicine
from models.customer import Customer

class DBManager:
    """
    Manages the SQLite database connection and operations for the PharmaCare application.
    Handles database initialization, table creation, and provides methods for
    basic CRUD operations (Create, Read, Update, Delete), including user authentication,
    medicine management, customer management, login email history, and sales.
    """
    def __init__(self, db_name="pharmacy.db"):
        """
        Initializes the DBManager with the specified database name.
        Connects to the database and ensures tables are created.
        """
        self.db_name = db_name
        self.conn = None
        self.connect_db()
        self.create_tables()

    def connect_db(self):
        """
        Establishes a connection to the SQLite database.
        If the database file does not exist, it will be created.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute("PRAGMA foreign_keys = ON")
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.show_error_message("Database Connection Error",
                                    f"Could not connect to the database: {e}")

    def close_db(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_tables(self):
        """
        Creates necessary tables in the database if they do not already exist.
        Tables include: users, medicines, sales, customers, and login_history.
        """
        if not self.conn:
            print("Cannot create tables: No database connection.")
            return

        cursor = self.conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Medicines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                low_stock_alert INTEGER DEFAULT 10,
                expiry_date TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                email TEXT UNIQUE,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sales table
        # items_json will store a JSON string of the items sold
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT,
                total_amount REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                items_json TEXT NOT NULL, -- Stores JSON string of sold items: [{"med_id": 1, "qty": 2, "price": 12.5, "name": "Paracetamol"}]
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
            )
        """)

        # login_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        print("Tables checked/created successfully.")

    def add_user(self, user):
        """Adds a new user to the 'users' table."""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
                (user.full_name, user.email, hashed_password.decode('utf-8'))
            )
            self.conn.commit()
            print(f"User '{user.email}' added successfully.")
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                self.show_error_message("Registration Error", "This email is already registered.")
            else:
                self.show_error_message("Database Error", f"Failed to add user: {e}")
            return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to add user: {e}")
            return False

    def get_user_by_email(self, email):
        """Retrieves a user's data from the 'users' table by their email address."""
        if not self.conn: return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, full_name, email, password, created_at FROM users WHERE email = ?", (email,))
            user_data = cursor.fetchone()
            return user_data
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to retrieve user: {e}")
            return None

    # --- Medicine Management Methods ---
    def add_medicine(self, medicine):
        """Adds a new medicine to the 'medicines' table."""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO medicines (name, brand, category, price, stock, low_stock_alert, expiry_date, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (medicine.name, medicine.brand, medicine.category, medicine.price,
                 medicine.stock, medicine.low_stock_alert, medicine.expiry_date, medicine.description)
            )
            self.conn.commit()
            print(f"Medicine '{medicine.name}' added successfully.")
            return True
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to add medicine: {e}")
            return False

    def get_all_medicines(self):
        """Retrieves all medicines from the 'medicines' table."""
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, brand, category, price, stock, low_stock_alert, expiry_date, description, created_at FROM medicines ORDER BY name ASC")
            rows = cursor.fetchall()
            return [Medicine.from_db_row(row) for row in rows]
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to retrieve medicines: {e}")
            return []

    def get_medicine_by_id(self, medicine_id):
        """
        Retrieves a single medicine by its ID.
        Returns a Medicine object or None if not found.
        """
        if not self.conn: return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, brand, category, price, stock, low_stock_alert, expiry_date, description, created_at FROM medicines WHERE id = ?", (medicine_id,))
            row = cursor.fetchone()
            if row:
                return Medicine.from_db_row(row)
            return None
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to retrieve medicine by ID: {e}")
            return None

    def update_medicine(self, medicine):
        """Updates an existing medicine record in the 'medicines' table."""
        if not self.conn: return False
        if medicine.id is None:
            self.show_error_message("Update Error", "Medicine ID is required to update a medicine.")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """UPDATE medicines SET name=?, brand=?, category=?, price=?, stock=?,
                   low_stock_alert=?, expiry_date=?, description=? WHERE id=?""",
                (medicine.name, medicine.brand, medicine.category, medicine.price,
                 medicine.stock, medicine.low_stock_alert, medicine.expiry_date,
                 medicine.description, medicine.id)
            )
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"Medicine ID {medicine.id} updated successfully.")
                return True
            else:
                self.show_error_message("Update Error", f"Medicine with ID {medicine.id} not found.")
                return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to update medicine: {e}")
            return False

    def update_medicine_stock(self, medicine_id, new_stock):
        """
        Updates the stock quantity for a specific medicine.

        Args:
            medicine_id (int): The ID of the medicine to update.
            new_stock (int): The new stock quantity.

        Returns:
            bool: True if stock was updated successfully, False otherwise.
        """
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE medicines SET stock = ? WHERE id = ?", (new_stock, medicine_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"Medicine ID {medicine_id} stock updated to {new_stock}.")
                return True
            else:
                self.show_error_message("Stock Update Error", f"Medicine with ID {medicine_id} not found for stock update.")
                return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to update medicine stock: {e}")
            return False


    def delete_medicine(self, medicine_id):
        """Deletes a medicine record from the 'medicines' table by its ID."""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM medicines WHERE id=?", (medicine_id,))
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"Medicine ID {medicine_id} deleted successfully.")
                return True
            else:
                self.show_error_message("Delete Error", f"Medicine with ID {medicine_id} not found.")
                return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to delete medicine: {e}")
            return False

    # --- Customer Management Methods ---
    def add_customer(self, customer):
        """Adds a new customer to the 'customers' table."""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                (customer.name, customer.phone, customer.email, customer.address)
            )
            self.conn.commit()
            print(f"Customer '{customer.name}' added successfully.")
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                self.show_error_message("Customer Error", "Phone or Email already exists for another customer.")
            else:
                self.show_error_message("Database Error", f"Failed to add customer: {e}")
            return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to add customer: {e}")
            return False

    def get_all_customers(self):
        """Retrieves all customers from the 'customers' table."""
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, phone, email, address, created_at FROM customers ORDER BY name ASC")
            rows = cursor.fetchall()
            return [Customer.from_db_row(row) for row in rows]
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to retrieve customers: {e}")
            return []

    def get_customer_by_id(self, customer_id):
        """
        Retrieves a single customer by their ID.
        Returns a Customer object or None if not found.
        """
        if not self.conn: return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, phone, email, address, created_at FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            if row:
                return Customer.from_db_row(row)
            return None
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to retrieve customer by ID: {e}")
            return None

    def update_customer(self, customer):
        """Updates an existing customer record in the 'customers' table."""
        if not self.conn: return False
        if customer.id is None:
            self.show_message("Update Error", "Customer ID is required to update a customer.")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?""",
                (customer.name, customer.phone, customer.email, customer.address, customer.id)
            )
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"Customer ID {customer.id} updated successfully.")
                return True
            else:
                self.show_error_message("Update Error", f"Customer with ID {customer.id} not found.")
                return False
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                self.show_error_message("Customer Error", "Phone or Email already exists for another customer.")
            else:
                self.show_error_message("Database Error", f"Failed to update customer: {e}")
            return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to update customer: {e}")
            return False

    def delete_customer(self, customer_id):
        """Deletes a customer record from the 'customers' table by its ID."""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"Customer ID {customer_id} deleted successfully.")
                return True
            else:
                self.show_error_message("Delete Error", f"Customer with ID {customer_id} not found.")
                return False
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to delete customer: {e}")
            return False

    # --- Login History Methods ---
    def add_login_email(self, email):
        """Adds or updates an email in the login_history table."""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO login_history (email, last_login) VALUES (?, CURRENT_TIMESTAMP)",
                (email,)
            )
            self.conn.commit()
            print(f"Login history updated for email: {email}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating login history for {email}: {e}")
            return False

    def get_login_emails(self):
        """Retrieves all emails from the login_history table, ordered by last_login descending."""
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT email FROM login_history ORDER BY last_login DESC")
            emails = [row[0] for row in cursor.fetchall()]
            return emails
        except sqlite3.Error as e:
            print(f"Error retrieving login emails: {e}")
            return []

    # --- New: Sales Management Methods ---

    def add_sale(self, customer_id, customer_name, customer_phone, customer_email, total_amount, items):
        """
        Adds a new sale record to the 'sales' table.
        Also updates the stock of sold medicines.

        Args:
            customer_id (int/None): ID of the customer, or None if not linked.
            customer_name (str): Name of the customer (even if not linked to ID).
            customer_phone (str): Phone of the customer (even if not linked to ID).
            customer_email (str): Email of the customer (even if not linked to ID).
            total_amount (float): Total amount of the sale.
            items (list): List of dictionaries, each representing a sold item:
                          [{"med_id": int, "qty": int, "price": float, "name": str}]

        Returns:
            bool: True if the sale was added successfully and stock updated, False otherwise.
        """
        if not self.conn:
            self.show_error_message("Database Error", "No database connection.")
            return False

        try:
            cursor = self.conn.cursor()
            # Start a transaction for atomicity
            self.conn.execute("BEGIN TRANSACTION")

            # Insert sale record
            items_json = json.dumps(items) # Convert items list to JSON string
            cursor.execute(
                """INSERT INTO sales (customer_id, customer_name, customer_phone, customer_email, total_amount, items_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (customer_id, customer_name, customer_phone, customer_email, total_amount, items_json)
            )
            sale_id = cursor.lastrowid # Get the ID of the newly inserted sale

            # Update medicine stock for each item sold
            for item in items:
                med_id = item['med_id']
                qty_sold = item['qty']
                # Get current stock
                cursor.execute("SELECT stock FROM medicines WHERE id = ?", (med_id,))
                current_stock_row = cursor.fetchone()
                if not current_stock_row:
                    raise ValueError(f"Medicine with ID {med_id} not found during stock update.")
                current_stock = current_stock_row[0]
                new_stock = current_stock - qty_sold
                if new_stock < 0:
                    raise ValueError(f"Insufficient stock for medicine ID {med_id}. Available: {current_stock}, Requested: {qty_sold}")

                cursor.execute("UPDATE medicines SET stock = ? WHERE id = ?", (new_stock, med_id))

            self.conn.commit() # Commit the transaction
            print(f"Sale ID {sale_id} recorded successfully and stock updated.")
            return True
        except ValueError as ve:
            self.conn.rollback() # Rollback if stock is insufficient
            self.show_error_message("Sale Error", str(ve))
            return False
        except sqlite3.Error as e:
            self.conn.rollback() # Rollback on any other database error
            self.show_error_message("Database Error", f"Failed to record sale: {e}")
            return False

    def get_all_sales(self):
        """
        Retrieves all sales records from the 'sales' table.
        The 'items_json' column will be parsed back into a Python list.

        Returns:
            list: A list of dictionaries, each representing a sale.
                  Returns an empty list if no sales are found or on error.
        """
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, customer_id, customer_name, customer_phone, customer_email, total_amount, sale_date, items_json FROM sales ORDER BY sale_date DESC")
            rows = cursor.fetchall()
            sales_data = []
            for row in rows:
                sale_dict = {
                    "id": row[0],
                    "customer_id": row[1],
                    "customer_name": row[2],
                    "customer_phone": row[3],
                    "customer_email": row[4],
                    "total_amount": row[5],
                    "sale_date": row[6],
                    "items": json.loads(row[7]) # Parse JSON string back to list
                }
                sales_data.append(sale_dict)
            return sales_data
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Failed to retrieve sales: {e}")
            return []


    def show_error_message(self, title, message):
        """
        Displays an error message box to the user.
        """
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

# Example usage (for testing DB connection and table creation)
if __name__ == "__main__":
    from models.user import User
    from models.medicine import Medicine
    from models.customer import Customer
    from PyQt6.QtWidgets import QApplication # For standalone test

    app = QApplication([]) # Initialize QApplication for QMessageBox
    db_manager = DBManager("test_pharmacy_full_sales.db") # Create a test database

    # Add some dummy data for testing
    print("\n--- Initializing Test Data ---")
    db_manager.add_user(User("Alice Smith", "alice@example.com", "password123"))
    db_manager.add_medicine(Medicine("Paracetamol 500mg", "Tylenol", "Pain Relief", 5.50, 100, expiry_date="2025-12-31"))
    db_manager.add_medicine(Medicine("Amoxicillin 250mg", "Amoxil", "Antibiotic", 12.75, 50, low_stock_alert=5, expiry_date="2024-10-15"))
    db_manager.add_customer(Customer(name="John Doe", phone="123-456-7890", email="john.doe@example.com", address="123 Main St"))

    # Retrieve added items to get their IDs
    meds = db_manager.get_all_medicines()
    customers = db_manager.get_all_customers()

    paracetamol_id = None
    amoxicillin_id = None
    john_doe_id = None

    for med in meds:
        if med.name == "Paracetamol 500mg":
            paracetamol_id = med.id
        elif med.name == "Amoxicillin 250mg":
            amoxicillin_id = med.id

    for cust in customers:
        if cust.name == "John Doe":
            john_doe_id = cust.id

    print(f"Paracetamol ID: {paracetamol_id}, Amoxicillin ID: {amoxicillin_id}, John Doe ID: {john_doe_id}")

    # --- Test Sales Management ---
    print("\n--- Testing Sales Management ---")

    if paracetamol_id and amoxicillin_id and john_doe_id:
        # Example sale 1: Linked to a customer
        items_sale1 = [
            {"med_id": paracetamol_id, "qty": 2, "price": 5.50, "name": "Paracetamol 500mg"},
            {"med_id": amoxicillin_id, "qty": 1, "price": 12.75, "name": "Amoxicillin 250mg"}
        ]
        total_sale1 = sum(item['qty'] * item['price'] for item in items_sale1)
        if db_manager.add_sale(john_doe_id, "John Doe", "123-456-7890", "john.doe@example.com", total_sale1, items_sale1):
            print(f"Sale 1 recorded for John Doe. Total: {total_sale1:.2f}")
        else:
            print("Sale 1 failed.")

        # Example sale 2: Walk-in customer
        items_sale2 = [
            {"med_id": paracetamol_id, "qty": 1, "price": 5.50, "name": "Paracetamol 500mg"}
        ]
        total_sale2 = sum(item['qty'] * item['price'] for item in items_sale2)
        if db_manager.add_sale(None, "Walk-in Customer", "", "", total_sale2, items_sale2):
            print(f"Sale 2 recorded for Walk-in Customer. Total: {total_sale2:.2f}")
        else:
            print("Sale 2 failed.")

        # Test insufficient stock
        items_sale3 = [
            {"med_id": paracetamol_id, "qty": 200, "price": 5.50, "name": "Paracetamol 500mg"} # Should fail
        ]
        total_sale3 = sum(item['qty'] * item['price'] for item in items_sale3)
        print("\nAttempting sale with insufficient stock...")
        if db_manager.add_sale(None, "Problem Customer", "", "", total_sale3, items_sale3):
            print("Sale 3 recorded (should have failed).")
        else:
            print("Sale 3 failed as expected due to insufficient stock.")

    else:
        print("Not enough initial data to run sales tests.")


    # Get all sales
    all_sales = db_manager.get_all_sales()
    print("\nAll Sales Records:")
    for sale in all_sales:
        print(f"Sale ID: {sale['id']}, Customer: {sale['customer_name']}, Total: {sale['total_amount']:.2f}, Items: {sale['items']}")

    print("\n--- Current Medicine Stock After Sales ---")
    updated_meds = db_manager.get_all_medicines()
    for med in updated_meds:
        print(f"{med.name}: Stock = {med.stock}")

    db_manager.close_db()
