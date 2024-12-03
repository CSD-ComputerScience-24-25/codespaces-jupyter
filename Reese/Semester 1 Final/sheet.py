from googleapiclient.discovery import build
from google.oauth2 import service_account
import sqlite3
import pandas as pd

# === Configuration ===
db_path = 'Reese/Final.sqlite'  # Replace with your SQLite file path
sheet_id = "1A5EL5e8NqLPtWlnkad39GRC5DR2DMJxS3TaYiMQh4nM"  # Replace with your Google Sheet ID
table_name = "inventory"  # Replace with your SQLite table name
service_account_file = 'path/to/service-account.json'  # Path to your Service Account JSON file

# === Initialize Google Sheets API with Service Account ===
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# === SQLite to Google Sheets ===
def export_sqlite_to_sheet():
    """Exports data from SQLite to Google Sheets."""
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Prepare data for Sheets API
    values = [df.columns.values.tolist()] + df.values.tolist()

    # Write data to Google Sheet
    body = {'values': values}
    sheet.values().update(
        spreadsheetId=sheet_id,
        range="Sheet1",  # Update this range if your sheet name is different
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"Exported {len(df)} rows from {table_name} to Google Sheets.")

# === Google Sheets to SQLite ===
def sync_sheet_to_sqlite():
    """Syncs data from Google Sheets to SQLite."""
    result = sheet.values().get(
        spreadsheetId=sheet_id,
        range="Sheet1"  # Update this range if your sheet name is different
    ).execute()
    values = result.get('values', [])
    if not values:
        print("No data found in the Google Sheet.")
        return

    # Convert data to DataFrame
    df = pd.DataFrame(values[1:], columns=values[0])

    # Write DataFrame to SQLite
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

    print(f"Synced {len(df)} rows from Google Sheets to {table_name} in SQLite.")

# === Main Function ===
if __name__ == "__main__":
    print("Choose an option:")
    print("1. Export SQLite to Google Sheets")
    print("2. Sync Google Sheets to SQLite")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        export_sqlite_to_sheet()
    elif choice == '2':
        sync_sheet_to_sqlite()
    else:
        print("Invalid choice. Exiting.")
