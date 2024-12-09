import sqlite3
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration
db_path = "/Users/reesedelaney/Downloads/codespaces-jupyter-main/Reese/Semester 1 Final/Reese\Final.sqlite"  # File path of Database
JSON_KEYFILE = '/Users/reesedelaney/Downloads/codespaces-jupyter-main/Reese/Semester 1 Final/service-account.json'  # Path to your service account JSON key file
SHEET_NAME = 'Grocery Store Inventory and Transactions'  # Name of your Google Sheet
WORKSHEET_NAME = 'sheet1'  # Worksheet/tab name in the Google Sheet

# Authenticate Google Sheets
def authenticate_google_sheets(json_keyfile):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    return gspread.authorize(credentials)

# Update Google Sheets with the latest inventory
def update_google_sheet(sheet, worksheet_name, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Inventory")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    worksheet = sheet.worksheet(worksheet_name)
    worksheet.clear()  # Clear existing data
    worksheet.append_row(columns)  # Write headers
    worksheet.append_rows(rows)  # Write data rows

# Function to log a transaction and update Google Sheets afterward
def log_transaction(item_id, transaction_type, quantity):
    connection = sqlite3.connect(db_path)
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

        # Log the transaction
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

        # Authenticate Google Sheets and push the updated inventory
        sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
        update_google_sheet(sheet, WORKSHEET_NAME, connection)
        print("Google Sheets updated with the new inventory.")

    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        connection.close()

# Main options
options = input('''
Choose one of the following options:
1 = Transaction Mode
2 = View Transaction History
3 = View Store Items
4 = Edit Store Items
Enter your choice: ''')

# Convert the input to an integer for comparison
try:
    options = int(options)
    if options == 1:
        print('Transaction Mode')
        item_id = int(input("Enter an Item ID: "))
        transaction_type = input("Enter transaction type (buy/sell): ").strip().lower()
        quantity = int(input("Enter Item Quantity: "))
        log_transaction(item_id, transaction_type, quantity)
    elif options == 2:
        print('View Transaction History')
    elif options == 3:
        print('View Store Items')
    elif options == 4:
        print('You can edit store items and inventory here: https://docs.google.com/spreadsheets/d/1A5EL5e8NqLPtWlnkad39GRC5DR2DMJxS3TaYiMQh4nM/edit?usp=sharing')
    else:
        print("Invalid option. Please choose a number between 1 and 4.")
except ValueError:
    print("Invalid input. Please enter a number.")
