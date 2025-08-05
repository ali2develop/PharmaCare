# database/db_manager.py

import sqlite3
from PyQt6.QtWidgets import QMessageBox

class DBManager:
    """
    Manages the SQLite database connection and operations for the PharmaCare application.
    Handles database initialization, table creation, and provides methods for
    basic CRUD operations (Create, Read, Update, Delete).
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
        Tables include: users, medicines, sales, and customers.
        """
        if not self.conn:
            print("Cannot create tables: No database connection.")
            return

        cursor = self.conn.cursor()

        # Users table for login/signup
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL, -- In a real app, store hashed passwords!
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
                expiry_date TEXT, -- YYYY-MM-DD format
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT,
                total_amount REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                items_json TEXT -- Stores JSON string of sold items: [{"med_id": 1, "qty": 2, "price": 12.5}]
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

        self.conn.commit()
        print("Tables checked/created successfully.")

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
    db_manager = DBManager("test_pharmacy.db") # Create a test database
    # You can add some dummy data insertion here to test
    # For example, adding a user:
    # try:
    #     cursor = db_manager.conn.cursor()
    #     cursor.execute("INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
    #                    ("Test User", "test@example.com", "hashed_password"))
    #     db_manager.conn.commit()
    #     print("Test user added.")
    # except sqlite3.IntegrityError:
    #     print("Test user already exists.")
    db_manager.close_db()
