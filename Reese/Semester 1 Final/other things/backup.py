import sqlite3
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import threading
import uuid
import os
import matplotlib.pyplot as plt


# Configuration/Paths
JSON_KEYFILE = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/service-account.json'  # Path to your service account JSON key file
DB_NAME = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/Reese\Final.sqlite'  # Name of your SQLite database
SHEET_NAME = 'Grocery Store Inventory and Transactions'  # Name of Google Sheet
INVENTORY_WORKSHEET_NAME = 'Inventory'  # Worksheet/tab name for inventory in the Google Sheet
TRANSACTION_WORKSHEET_NAME = 'Transactions'  # Worksheet/tab name for transactions in the Google Sheet
INVENTORY_TABLE_NAME = 'inventory'  # SQLite inventory table name
TRANSACTION_TABLE_NAME = 'Transactions' #SQLite Transactions table name
SYNC_INTERVAL = 5  # Interval in seconds between each sync

# Global event to stop the background sync
stop_sync_event = threading.Event()

# Authenticate Google Sheets
def authenticate_google_sheets(json_keyfile):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    return gspread.authorize(credentials)

# Connect to SQLite database
def connect_sqlite(db_name):
    return sqlite3.connect(db_name)

# Fetch data from Google Sheets
def fetch_sheet_data(sheet, worksheet_name):
    worksheet = sheet.worksheet(worksheet_name)
    return worksheet.get_all_records()  # Returns data as a list of dictionaries

# Update SQLite database inventory and Transactions from Google Sheets
def update_sqlite_from_sheet(conn, table_name, sheet_data):
    cursor = conn.cursor()

    if not sheet_data:
        cursor.execute(f"DELETE FROM {table_name}")  # Delete all rows from the table if no data
        conn.commit()
        return  # Skip inserting new data since the table is cleared

    # Process the data and insert into SQLite if sheet data is available
    columns = ", ".join(sheet_data[0].keys())
    placeholders = ", ".join("?" * len(sheet_data[0]))
    cursor.execute(f"DELETE FROM {table_name}")  # Optional: Clear table before inserting new data (if you want to replace existing data)
    
    for row in sheet_data:
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", tuple(row.values()))
    
    conn.commit()


# Update SQLite database transactions from Google Sheets
def update_transactions_from_sheet(conn, sheet):
    cursor = conn.cursor()
    sheet_data = fetch_sheet_data(sheet, TRANSACTION_WORKSHEET_NAME)

    # Fetch existing transactions in the database
    cursor.execute("SELECT transaction_id FROM Transactions")
    db_transactions = cursor.fetchall()
    db_transaction_ids = set((row[0] for row in db_transactions))

    # Synchronize sheet data to database
    for row in sheet_data:
        # Ensure the row has the 'transaction_id' key
        if 'transaction_id' not in row or not row['transaction_id']:
            print(f"Skipping row due to missing 'transaction_id': {row}")
            continue

        if row['transaction_id'] not in db_transaction_ids:
            cursor.execute(
                """
                INSERT INTO Transactions (transaction_id, item_id, transaction_type, quantity, transaction_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row['transaction_id'],
                    row.get('item_id', None),
                    row.get('transaction_type', None),
                    row.get('quantity', 0),
                    row.get('transaction_date', None),
                ),
            )

    # Remove transactions in the database that are no longer in the sheet
    sheet_transaction_ids = set((row['transaction_id'] for row in sheet_data if 'transaction_id' in row))
    transactions_to_remove = db_transaction_ids - sheet_transaction_ids

    for transaction_id in transactions_to_remove:
        cursor.execute("DELETE FROM Transactions WHERE transaction_id = ?", (transaction_id,))

    conn.commit()

def initialize_db(conn):
    cursor = conn.cursor()
    
    # Create inventory table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT,
            quantity INTEGER,
            item_price REAL
        )
    """)
    
    # Create Transactions table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id TEXT PRIMARY KEY,
            item_id INTEGER,
            transaction_type TEXT,
            quantity INTEGER,
            transaction_date TEXT,
            FOREIGN KEY (item_id) REFERENCES inventory (item_id)
        )
    """)
    
    conn.commit()


# Sheet sync in background
def sheet_sync():
    sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
    conn = connect_sqlite(DB_NAME)
    initialize_db(conn)  # Ensure the table exists before syncing

    try:
        while not stop_sync_event.is_set():
            sheet_data = fetch_sheet_data(sheet, INVENTORY_WORKSHEET_NAME)
            update_sqlite_from_sheet(conn, INVENTORY_TABLE_NAME, sheet_data)
            sheet_data = fetch_sheet_data(sheet, TRANSACTION_WORKSHEET_NAME)
            update_sqlite_from_sheet(conn, TRANSACTION_TABLE_NAME, sheet_data)
            time.sleep(SYNC_INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()


# Update Google Sheets with a new transaction
def update_google_sheet_summary_transaction(transaction_id, item_id_list, total_quantity, total_price, transaction_date):
    try:
        sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
        worksheet = sheet.worksheet(TRANSACTION_WORKSHEET_NAME)

        # Prepare the new row
        new_row = [
            transaction_id,  # Transaction ID
            item_id_list,     # Comma-separated list of item IDs
            total_quantity,   # Total quantity of items purchased
            total_price,      # Total price for the transaction
            transaction_date.strftime('%Y-%m-%d %H:%M:%S')  # Transaction Date
        ]

        # Append the new row to the Google Sheet
        worksheet.append_row(new_row)
        print(f"Transaction logged in Google Sheets: {new_row}")

    except Exception as e:
        print(f"An error occurred while updating Google Sheets: {e}")

#update inventory
def update_google_sheet_inventory():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch all inventory data from the database
        cursor.execute("SELECT item_id, item_name, quantity, item_price FROM inventory")
        inventory_data = cursor.fetchall()

        # Authenticate and open the Google Sheet
        sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
        worksheet = sheet.worksheet(INVENTORY_WORKSHEET_NAME)

        # Clear the current content of the worksheet (optional but recommended for accurate sync)
        worksheet.clear()

        # Define the header row
        header = ["item_id", "item_name", "quantity", "item_price"]
        worksheet.append_row(header)

        # Append all inventory rows
        for row in inventory_data:
            worksheet.append_row(list(row))

        print("Inventory updated in Google Sheets.")

    except Exception as e:
        print(f"An error occurred while updating Google Sheets inventory: {e}")

    finally:
        conn.close()


# Log a transaction and update Google Sheets afterward
def log_transaction(items):
    connection = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    total_price = 0
    total_quantity = 0
    item_ids = []

    try:
        transaction_id = str(uuid.uuid4())
        transaction_date = datetime.now()

        for item_id, quantity in items.items():
            cursor.execute("SELECT quantity, item_price FROM Inventory WHERE item_id = ?", (item_id,))
            result = cursor.fetchone()
            if not result:
                print(f"Item with ID {item_id} does not exist.")
                return

            current_quantity, item_price = result
            if quantity > current_quantity:
                print(f"Not enough stock for item {item_id}. Current stock: {current_quantity}.")
                return

            new_quantity = current_quantity - quantity
            total_price += quantity * item_price
            total_quantity += quantity
            item_ids.append(str(item_id))

            cursor.execute("UPDATE Inventory SET quantity = ? WHERE item_id = ?", (new_quantity, item_id))

            cursor.execute("""
                INSERT OR IGNORE INTO Transactions (transaction_id, item_id, transaction_type, quantity, transaction_date)
                VALUES (?, ?, ?, ?, ?)
            """, (transaction_id, item_id, "sell", quantity, transaction_date))

        connection.commit()

        item_id_list = ", ".join(item_ids)
        formatted_total_price = f"${total_price:.2f}"

        update_google_sheet_summary_transaction(transaction_id, item_id_list, total_quantity, formatted_total_price, transaction_date)

        # Sync inventory with Google Sheets
        update_google_sheet_inventory()

        print(f"Transaction ID: {transaction_id} logged successfully.")
        print(f"Total Quantity: {total_quantity} items.")
        print(f"Total Price: {formatted_total_price}")

    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        connection.close()


#view sales stats with matplotlib
def view_sales_stats():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # SQL query to aggregate sales by date
        query = """
        SELECT transaction_type, SUM(quantity) AS total_quantity, DATE(transaction_date) AS date
        FROM Transactions
        WHERE transaction_type = 'sell'
        GROUP BY DATE(transaction_date)
        ORDER BY DATE(transaction_date)
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("No sales data available.")
            return

        # Extract dates and quantities
        dates = [row[2] for row in rows]
        quantities = [row[1] for row in rows]

        if not dates or not quantities:
            print("No valid sales data to plot.")
            return

        # Create directory for the sales stats image if it doesn't exist
        output_dir = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/sales images'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # Create the directory if it doesn't exist

        # Generate the plot
        plt.figure(figsize=(10, 6))
        plt.plot(dates, quantities, marker='o', linestyle='-', color='b')
        plt.title("Total Sales Over Time")
        plt.xlabel("Date")
        plt.ylabel("Total Quantity Sold")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Save the plot as a PNG file in the 'sales_stats_images' folder
        image_path = os.path.join(output_dir, 'sales_stats.png')
        plt.savefig(image_path)
        plt.close()

        print(f"Sales stats graph saved as '{image_path}'. Open this file to view the graph.")

    except Exception as e:
        print(f"An error occurred while generating sales statistics: {e}")
    finally:
        conn.close()

def view_sales_stats_24_hours():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Ask the user for a specific date (e.g., "2024-12-16") or use the current date
        specific_date = input("Enter a specific date (YYYY-MM-DD) for the sales stats, or press Enter to use today: ")
        if not specific_date:
            specific_date = datetime.now().strftime('%Y-%m-%d')

        # SQL query to get sales per hour for a specific day
        query = """
        SELECT 
            strftime('%H', transaction_date) AS hour, 
            SUM(quantity) AS total_quantity
        FROM Transactions
        WHERE transaction_type = 'sell'
        AND DATE(transaction_date) = ?
        GROUP BY hour
        ORDER BY hour
        """
        cursor.execute(query, (specific_date,))
        rows = cursor.fetchall()

        if not rows:
            print(f"No sales data available for {specific_date}.")
            return

        # Extract hours and quantities
        hours = [row[0] for row in rows]
        quantities = [row[1] for row in rows]

        if not hours or not quantities:
            print("No valid sales data to plot.")
            return

        # Create the plot for sales over the course of the day
        plt.figure(figsize=(10, 6))
        plt.plot(hours, quantities, marker='o', linestyle='-', color='b')
        plt.title(f"Total Sales on {specific_date} by Hour")
        plt.xlabel("Hour of the Day")
        plt.ylabel("Total Quantity Sold")
        plt.xticks(range(0, 24))  # Set x-axis to show hours from 0 to 23
        plt.grid(True)
        plt.tight_layout()

        # Save the plot as a PNG file
        output_dir = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/sales images'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        image_path = os.path.join(output_dir, f'sales_stats_{specific_date}.png')
        plt.savefig(image_path)
        plt.close()

        print(f"Sales stats graph for {specific_date} saved as '{image_path}'. Open this file to view the graph.")

    except Exception as e:
        print(f"An error occurred while generating sales statistics: {e}")
    finally:
        conn.close()

# View Inventory (Database)
def verify_inventory():
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT * FROM inventory"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    print("Database Contents:")
    print(columns)
    for row in rows:
        print(row)
    conn.close()

def view_transactions():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT transaction_id, item_id, quantity, transaction_date FROM Transactions;"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("No transactions found.")
            return

        columns = [description[0] for description in cursor.description]
        print(f"{' | '.join(columns)}")
        print("-" * 50)

        for row in rows:
            print(" | ".join(str(value) for value in row))
    except Exception as e:
        print(f"An error occurred while viewing transactions: {e}")
    finally:
        conn.close()

# Main options
def main():
    sync_thread = threading.Thread(target=sheet_sync)
    sync_thread.daemon = True
    sync_thread.start()

    while True:
        options = input('''
Choose one of the following options:
1 = Transaction Mode
2 = View Transaction History
3 = View Store Items
4 = Edit Store Items
5 = View Sales Stats
6 = Exit
Enter your choice: ''')

        try:
            options = int(options)
            if options == 1:
                print('Transaction Mode')
                stop_sync_event.set()
                print("View Item ID's: https://tinyurl.com/fejfe9r39")
                items = {}
                while True:
                    try:
                        item_id = int(input("Enter Item ID (or 0 to finish): "))
                        if item_id == 0:
                            break
                        quantity = int(input("Enter Quantity: "))
                        if item_id in items:
                            items[item_id] += quantity
                        else:
                            items[item_id] = quantity
                    except ValueError:
                        print("Invalid input. Try again.")
                if items:
                    log_transaction(items)
                else:
                    print("No items to process.")
                stop_sync_event.clear()
                if not sync_thread or not sync_thread.is_alive():
                    sync_thread = threading.Thread(target=sheet_sync)
                    sync_thread.daemon = True
                    sync_thread.start()
            elif options == 2:
                print('View Transaction History')
                view_transactions()
            elif options == 3:
                print('View Store Items')
                verify_inventory()
            elif options == 4:
                print('You can edit store items and inventory here: https://docs.google.com/spreadsheets/d/1A5EL5e8NqLPtWlnkad39GRC5DR2DMJxS3TaYiMQh4nM/edit?usp=sharing')
            elif options == 5:
                reports = input('''
Choose one of the following options:
1 = View Transaction Stats For a Specfic Day
2 = View All-Time Transaction Stats
Enter your choice: ''')
                if reports == 1:
                    view_sales_stats_24_hours()
                elif reports == 2:
                    view_sales_stats
                print('Graph saved as image successfully!')
            elif options == 6:
                break
            else:
                print("Invalid option. Please choose a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
    