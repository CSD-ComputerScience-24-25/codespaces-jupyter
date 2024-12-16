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
TABLE_NAME = 'inventory'  # SQLite table name
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

# Update SQLite database from Google Sheets
def update_sqlite_from_sheet(conn, table_name, sheet_data):
    cursor = conn.cursor()
    columns = ", ".join(sheet_data[0].keys())
    placeholders = ", ".join("?" * len(sheet_data[0]))
    cursor.execute(f"DELETE FROM {table_name}")  # Clear table before syncing
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

# Sheet sync in background
def sheet_sync():
    sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
    conn = connect_sqlite(DB_NAME)
    try:
        while not stop_sync_event.is_set():  # Check if the stop flag is set
            sheet_data = fetch_sheet_data(sheet, INVENTORY_WORKSHEET_NAME)
            update_sqlite_from_sheet(conn, TABLE_NAME, sheet_data)
            update_transactions_from_sheet(conn, sheet)
            time.sleep(SYNC_INTERVAL)  # Wait for the next sync cycle
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()

# Update Google Sheets with a new transaction
def update_google_sheet_transaction(transaction_id, item_id, transaction_type, quantity, transaction_date):
    try:
        sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
        worksheet = sheet.worksheet(TRANSACTION_WORKSHEET_NAME)

        # Append the transaction as a new row
        new_row = [transaction_id, item_id, transaction_type, quantity, transaction_date.strftime('%Y-%m-%d %H:%M:%S')]
        worksheet.append_row(new_row)
        print(f"Transaction logged in Google Sheets: {new_row}")
    except Exception as e:
        print(f"An error occurred while updating Google Sheets: {e}")

# Log a transaction and update Google Sheets afterward
def log_transaction(item_id, transaction_type, quantity):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    try:
        # Check if item exists
        cursor.execute("SELECT quantity FROM Inventory WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()
        if not result:
            print(f"Item with ID {item_id} does not exist.")
            return

        current_quantity = int(result[0])

        # Update quantity based on transaction type
        if transaction_type.lower() == "sell":
            if quantity > current_quantity:
                print(f"Not enough stock to sell {quantity}. Current stock: {current_quantity}.")
                return
            new_quantity = current_quantity - quantity
        elif transaction_type.lower() == "buy":
            new_quantity = current_quantity + quantity
        else:
            print("Invalid transaction type. Use 'buy' or 'sell'.")
            return

        # Generate unique transaction_id
        transaction_id = str(uuid.uuid4())

        # Log transaction in the database
        transaction_date = datetime.now()
        cursor.execute("""
            INSERT INTO Transactions (transaction_id, item_id, transaction_type, quantity, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_id, item_id, transaction_type, quantity, transaction_date))

        # Update inventory in the database
        cursor.execute("""
            UPDATE Inventory
            SET quantity = ?
            WHERE item_id = ?
        """, (new_quantity, item_id))

        connection.commit()
        print(f"Transaction logged: {transaction_type} {quantity} units of item {item_id}. New stock: {new_quantity}. Transaction ID: {transaction_id}")

        # Update Google Sheets
        update_google_sheet_transaction(transaction_id, item_id, transaction_type, quantity, transaction_date)

        sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
        worksheet = sheet.worksheet(INVENTORY_WORKSHEET_NAME)
        rows = worksheet.get_all_records()
        for index, row in enumerate(rows, start=2):
            if str(row['item_id']) == str(item_id):  # Ensure both are strings
                worksheet.update_cell(index, list(row.keys()).index('quantity') + 1, new_quantity)
                print(f"Google Sheets inventory updated for item {item_id}.")
                break
    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        connection.close()

def view_transactions():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT * FROM Transactions"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("No transactions found.")
            return

        # Print column names
        columns = [description[0] for description in cursor.description]
        print(f"{' | '.join(columns)}")
        print("-" * 50)

        # Print rows
        for row in rows:
            print(" | ".join(str(value) for value in row))
    except Exception as e:
        print(f"An error occurred while viewing transactions: {e}")
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
                item_id = int(input("Enter an Item ID: "))
                transaction_type = "sell"
                quantity = int(input("Enter Item Quantity: "))
                log_transaction(item_id, transaction_type, quantity)
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

