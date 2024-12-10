import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sqlite3
import time

# Configuration
JSON_KEYFILE = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/service-account.json'  # Path to your service account JSON key file
DB_NAME = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final/Reese\Final.sqlite'                      # Name of your SQLite database
SHEET_NAME = 'Grocery Store Inventory and Transactions'         # Name of your Google Sheet
WORKSHEET_NAME = 'Inventory'                     # Worksheet/tab name in the Google Sheet
TABLE_NAME = 'inventory'                      # SQLite table name
SYNC_INTERVAL = 5  # Interval in seconds between each sync

# Authenticate Google Sheets
def authenticate_google_sheets(json_keyfile):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    return gspread.authorize(credentials)

# Connect to SQLite database
def connect_sqlite(db_name):
    conn = sqlite3.connect(db_name)
    return conn

# Fetch data from Google Sheets
def fetch_sheet_data(sheet, worksheet_name):
    worksheet = sheet.worksheet(worksheet_name)
    return worksheet.get_all_records()  # Returns data as a list of dictionaries

# Update SQLite database from Google Sheets
def update_sqlite_from_sheet(conn, table_name, sheet_data):
    cursor = conn.cursor()
    
    # Assuming columns match Google Sheets headers
    columns = ", ".join(sheet_data[0].keys())
    placeholders = ", ".join("?" * len(sheet_data[0]))

    # Update database
    cursor.execute(f"DELETE FROM {table_name}")  # Clear table before syncing
    for row in sheet_data:
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", tuple(row.values()))
    
    conn.commit()

# Update Google Sheets from SQLite database
def update_sheet_from_sqlite(sheet, worksheet_name, conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    worksheet = sheet.worksheet(worksheet_name)
    worksheet.clear()  # Clear existing data
    worksheet.append_row(columns)  # Write headers
    worksheet.append_rows(rows)  # Write data rows

# Main function
def main():
    # Authenticate and connect
    print("Authenticating Google Sheets...")
    sheet = authenticate_google_sheets(JSON_KEYFILE).open(SHEET_NAME)
    conn = connect_sqlite(DB_NAME)

    try:
        while True:
            # Sync Google Sheets to SQLite
            print("Fetching data from Google Sheets...")
            sheet_data = fetch_sheet_data(sheet, WORKSHEET_NAME)
            print("Updating SQLite database...")
            update_sqlite_from_sheet(conn, TABLE_NAME, sheet_data)

            # Sync SQLite to Google Sheets (optional)
            print("Fetching data from SQLite...")
            update_sheet_from_sqlite(sheet, WORKSHEET_NAME, conn, TABLE_NAME)

            print("Sync complete! Waiting for the next sync...")
            time.sleep(SYNC_INTERVAL)  # Wait for the specified interval
    except KeyboardInterrupt:
        print("Sync stopped manually.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()