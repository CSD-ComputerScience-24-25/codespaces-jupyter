import sqlite3
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import threading

# Configuration
JSON_KEYFILE = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/service-account.json'  # Path to your service account JSON key file
DB_NAME = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/Reese\Final.sqlite'  # Name of your SQLite database
db_path = "/workspaces/codespaces-jupyter/Reese/Semester 1 Final/Reese\Final.sqlite"  # File path of Database
SHEET_NAME = 'Grocery Store Inventory and Transactions'  # Name of your Google Sheet
WORKSHEET_NAME = 'Inventory'  # Worksheet/tab name in the Google Sheet
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

# Sheet sync in background
# Sheet sync in background
def sheet_sync():
    sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
    conn = connect_sqlite(DB_NAME)
    try:
        while not stop_sync_event.is_set():  # Check if the stop flag is set
            # Commented out or removed unnecessary print statements
            # print("Fetching data from Google Sheets...")
            sheet_data = fetch_sheet_data(sheet, WORKSHEET_NAME)
            # print("Updating SQLite database...")
            update_sqlite_from_sheet(conn, TABLE_NAME, sheet_data)
            # print("Sync complete. Waiting for the next sync...")
            time.sleep(SYNC_INTERVAL)  # Wait for the next sync cycle
    except KeyboardInterrupt:
        # You can choose to print if needed for debugging, or remove it for clean output
        # print("Sync stopped manually.")
        pass
    finally:
        conn.close()


# Log a transaction and update Google Sheets afterward
# Log a transaction and update Google Sheets afterward
def log_transaction(item_id, transaction_type, quantity):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    try:
        # Check if the item exists and get the current quantity
        cursor.execute("SELECT quantity FROM Inventory WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()

        if not result:
            print(f"Item with ID {item_id} does not exist.")
            return
        
        current_quantity = int(result[0])

        # Adjust the quantity based on the transaction type
        if transaction_type.lower() == "sell":
            if quantity > current_quantity:
                print(f"Not enough stock to sell {quantity} units. Current stock: {current_quantity}.")
                return
            new_quantity = current_quantity - quantity
        elif transaction_type.lower() == "buy":
            new_quantity = current_quantity + quantity
        else:
            print(f"Invalid transaction type: {transaction_type}. Use 'buy' or 'sell'.")
            return

        # Log the transaction in the SQLite database
        cursor.execute("""
            INSERT INTO Transactions (item_id, transaction_type, quantity, transaction_date)
            VALUES (?, ?, ?, ?)
        """, (item_id, transaction_type, quantity, datetime.now()))

        # Update the quantity in the Inventory table
        cursor.execute("""
            UPDATE Inventory
            SET quantity = ?
            WHERE item_id = ?
        """, (new_quantity, item_id))

        connection.commit()
        print(f"Transaction logged successfully: {transaction_type} {quantity} units of item {item_id}. New stock: {new_quantity}.")

        # Now, update the Google Sheets with the new inventory values
        sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
        worksheet = sheet.worksheet(WORKSHEET_NAME)
        
        # Find the row in the sheet that corresponds to the item_id
        rows = worksheet.get_all_records()  # Fetch all rows in the sheet
        item_row = None
        for row in rows:
            if row['item_id'] == item_id:
                item_row = row
                break
        
        if item_row:
            # Update the corresponding row in Google Sheets with the new quantity
            cell = worksheet.find(str(item_id))  # Find the cell with the item_id
            row_num = cell.row
            col_num = worksheet.find("quantity").col  # Find the column number for 'quantity'
            worksheet.update_cell(row_num, col_num, new_quantity)  # Update the quantity in Google Sheets
            print(f"Google Sheets updated with new quantity for item {item_id}.")
        else:
            print(f"Item with ID {item_id} not found in the Google Sheet.")

    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        connection.close()

# Main options
def main():
    # Start sheet sync in background
    sync_thread = threading.Thread(target=sheet_sync)
    sync_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
    sync_thread.start()

    # Main menu for user input
    while True:
        options = input('''
Choose one of the following options:
1 = Transaction Mode
2 = View Transaction History
3 = View Store Items
4 = Edit Store Items
5 = Exit
Enter your choice: ''')

        try:
            options = int(options)
            if options == 1:
                print('Transaction Mode')
                stop_sync_event.set()  # Stop background sync
                item_id = int(input("Enter an Item ID: "))
                transaction_type = input("Enter transaction type (buy/sell): ").strip().lower()
                quantity = int(input("Enter Item Quantity: "))
                log_transaction(item_id, transaction_type, quantity)
                stop_sync_event.clear()  # Clear the stop flag
                if not sync_thread or not sync_thread.is_alive():
                    sync_thread = threading.Thread(target=sheet_sync)
                    sync_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
                    sync_thread.start()
            elif options == 2:
                print('View Transaction History')
            elif options == 3:
                print('View Store Items')
            elif options == 4:
                print('You can edit store items and inventory here: https://docs.google.com/spreadsheets/d/1A5EL5e8NqLPtWlnkad39GRC5DR2DMJxS3TaYiMQh4nM/edit?usp=sharing')
            elif options == 5:
                break
            else:
                print("Invalid option. Please choose a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
