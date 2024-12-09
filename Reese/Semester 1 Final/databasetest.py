import sqlite3
from datetime import datetime

db_path = "/workspaces/codespaces-jupyter/Reese/Semester 1 Final/Reese\Final.sqlite"  # Update with your actual file path

# Connect to the database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# SQL statement to create the Transactions table
create_table_sql = """
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES Inventory(item_id)
);
"""

try:
    # Execute the statement
    cursor.execute(create_table_sql)
    connection.commit()
    print("Transactions table created successfully.")
except Exception as e:
    connection.rollback()
    print(f"An error occurred: {e}")
finally:
    connection.close()
