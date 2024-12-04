import sqlite3
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time

# Paths to your files
db_path = "Reese/Final.sqlite"  # SQLite database path
service_account_file = "/workspaces/codespaces-jupyter/Reese/Semester 1 Final/service-account.json"  # Google Service Account JSON file
spreadsheet_id = "1A5EL5e8NqLPtWlnkad39GRC5DR2DMJxS3TaYiMQh4nM"  # Replace with your Google Sheet ID
sheet_name = "Sheet1"  # Replace with your sheet name

# Function to export SQLite data to Google Sheets
def export_sqlite_to_sheet():
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM inventory"  # Replace 'inventory' with your table name
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Authenticate with Google Sheets API
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)
        service = build("sheets", "v4", credentials=creds)
        
        # Prepare data for Google Sheets
        values = [df.columns.tolist()] + df.values.tolist()
        body = {"values": values}
        
        # Write to Google Sheets
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body=body
        ).execute()
        
        print("Exported data to Google Sheets successfully!")
    except Exception as e:
        print(f"Error exporting to Google Sheets: {e}")

# Function to sync data from Google Sheets to SQLite
def sync_sheet_to_sqlite():
    try:
        # Authenticate with Google Sheets API
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)
        service = build("sheets", "v4", credentials=creds)
        
        # Read data from Google Sheets
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1:Z1000"  # Adjust range as needed
        ).execute()
        values = result.get("values", [])
        
        if not values:
            print("No data found in the Google Sheet.")
            return
        
        # Convert Google Sheets data to a DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        
        # Write data to SQLite
        conn = sqlite3.connect(db_path)
        df.to_sql("inventory", conn, if_exists="replace", index=False)  # Replace 'inventory' with your table name
        conn.close()
        
        print("Synced data from Google Sheets to SQLite successfully!")
    except Exception as e:
        print(f"Error syncing from Google Sheets: {e}")

# Main function to continuously sync
def main():
    while True:
        print("Starting sync...")
        
        try:
            export_sqlite_to_sheet()
            sync_sheet_to_sqlite()
        except Exception as e:
            print(f"Sync error: {e}")
        
        print("Sync complete. Waiting for next sync...")
        time.sleep(5)  # Sync interval in seconds (adjust as needed)

if __name__ == "__main__":
    main()