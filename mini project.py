import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

class CafeManagement:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Cafe Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#F5F5F5")

        # Database setup
        self.conn = self.connect_to_database()
        self.cursor = self.conn.cursor()
        self.setup_database()

        # Initialize GUI
        self.create_widgets()
        self.root.mainloop()

    def connect_to_database(self):
        """Connect to the MySQL database."""
        try:
            conn = mysql.connector.connect(
                host="localhost",  # Replace with your MySQL server hostname
                user="root",       # Replace with your MySQL username
                password="1410",  # Replace with your MySQL password
                database="cafe_db"    # Replace with your database name
            )
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {err}")
            exit()

    def setup_database(self):
        """Set up the MySQL database for storing menu and transactions."""
        # Create database if it doesn't exist
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS cafe_db")
        self.cursor.execute("USE cafe_db")

        # Create tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                                item_id INT AUTO_INCREMENT PRIMARY KEY,
                                name VARCHAR(255) UNIQUE NOT NULL,
                                price FLOAT NOT NULL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                trans_id INT AUTO_INCREMENT PRIMARY KEY,
                                total FLOAT NOT NULL,
                                timestamp DATETIME NOT NULL)''')

        # Populate menu items if empty
        default_items = [("Tea", 10), ("Coffee", 20), ("Sandwich", 50),
                         ("Cake", 100), ("Burger", 50), ("Pizza", 150),
                         ("Fries", 80), ("Pepsi", 80)]
        self.cursor.executemany('''INSERT IGNORE INTO menu (name, price) VALUES (%s, %s)''', default_items)
        self.conn.commit()

    def create_widgets(self):
        """Create all GUI widgets."""
        # Title
        title_label = tk.Label(self.root, text="Cafe Management System", font=("Arial", 24, "bold"), bg="#F5F5F5", fg="#2E8B57")
        title_label.pack(pady=10)

        # Date and Time
        datetime_label = tk.Label(self.root, text=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                   font=("Arial", 14), bg="#F5F5F5", fg="#2E8B57")
        datetime_label.pack()

        # Menu Frame
        menu_frame = ttk.LabelFrame(self.root, text="Menu", padding=(20, 10))
        menu_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.menu_items = {}
        self.load_menu(menu_frame)

        # Billing Section
        billing_frame = ttk.LabelFrame(self.root, text="Billing", padding=(20, 10))
        billing_frame.pack(side=tk.RIGHT, padx=20, pady=20)

        self.total_cost = tk.StringVar(value="0")
        total_label = tk.Label(billing_frame, text="Total:", font=("Arial", 16))
        total_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        total_entry = ttk.Entry(billing_frame, textvariable=self.total_cost, font=("Arial", 16), state="readonly")
        total_entry.grid(row=0, column=1, padx=5, pady=5)

        calculate_button = ttk.Button(billing_frame, text="Calculate Total", command=self.calculate_total)
        calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

        pay_button = ttk.Button(billing_frame, text="Complete Payment", command=self.complete_payment)
        pay_button.grid(row=2, column=0, columnspan=2, pady=10)

        clear_button = ttk.Button(billing_frame, text="Clear All", command=self.clear_entries)
        clear_button.grid(row=3, column=0, columnspan=2, pady=10)

        exit_button = ttk.Button(self.root, text="Exit", command=self.root.quit)
        exit_button.pack(side=tk.BOTTOM, pady=10)

    def load_menu(self, parent):
        """Load menu items from the database and create widgets dynamically."""
        self.cursor.execute("SELECT name, price FROM menu")
        menu_items = self.cursor.fetchall()

        for idx, (name, price) in enumerate(menu_items):
            label = tk.Label(parent, text=f"{name} - ₹{price}", font=("Arial", 14))
            label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")

            entry = ttk.Entry(parent, width=5)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.menu_items[name] = (price, entry)

    def calculate_total(self):
        """Calculate the total bill."""
        total = 0
        for name, (price, entry) in self.menu_items.items():
            try:
                quantity = int(entry.get())
                total += price * quantity
            except ValueError:
                continue

        self.total_cost.set(f"{total:.2f}")

    def complete_payment(self):
        """Save the transaction and display a message."""
        total = float(self.total_cost.get())
        if total == 0:
            messagebox.showwarning("Payment", "Please select items to calculate the total.")
            return

        # Save transaction
        timestamp = datetime.now()
        self.cursor.execute("INSERT INTO transactions (total, timestamp) VALUES (%s, %s)", (total, timestamp))
        self.conn.commit()

        messagebox.showinfo("Payment", f"Payment of ₹{total:.2f} completed successfully!")
        self.clear_entries()

    def clear_entries(self):
        """Clear all input fields."""
        for _, (_, entry) in self.menu_items.items():
            entry.delete(0, tk.END)
        self.total_cost.set("0")

    def __del__(self):
        """Close database connection on exit."""
        self.conn.close()


if __name__ == "__main__":
    CafeManagement()
