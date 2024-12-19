import sqlite3
from datetime import datetime
import uuid

DB_NAME = '/Users/reesedelaney/Downloads/codespaces-jupyter-main/Reese/Semester 1 Final/Reese\Final.sqlite'

def test_transaction_insert():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    transaction_id = str(uuid.uuid4())
    item_id = 1  # Replace with a valid item_id in your database
    transaction_type = 'sell'
    quantity = 10
    transaction_date = datetime.now()

    print(f"Testing transaction insert with UUID: {transaction_id}")

    try:
        cursor.execute("""
            INSERT INTO Transactions (transaction_id, item_id, transaction_type, quantity, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_id, item_id, transaction_type, quantity, transaction_date))
        conn.commit()
        print("Transaction inserted successfully.")
    except sqlite3.Error as e:
        print("SQLite Error:", e)
    finally:
        conn.close()

test_transaction_insert()
