import sqlite3

# Path to your SQLite database
db_path = 'Reese/Final.sqlite'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert sample data into 'inventory'
cursor.execute("INSERT INTO inventory (item_id, name, price, quantity) VALUES (1, 'Apple', 0.5, 100);")
cursor.execute("INSERT INTO inventory (item_id, name, price, quantity) VALUES (2, 'Banana', 0.3, 200);")

# Insert sample data into 'transactions'
cursor.execute("INSERT INTO transactions (transaction_id, item_id, type, quantity, date) VALUES (1, 1, 'sale', 10, '2024-12-03');")
cursor.execute("INSERT INTO transactions (transaction_id, item_id, type, quantity, date) VALUES (2, 2, 'purchase', 50, '2024-12-02');")

# Commit and close
conn.commit()
conn.close()

print("Sample data inserted successfully!")
