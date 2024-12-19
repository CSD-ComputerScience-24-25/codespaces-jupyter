import sqlite3

def fetch_data_from_sqlite():
    try:
        conn = sqlite3.connect('/Users/reesedelaney/Downloads/codespaces-jupyter-main/Reese/Semester 1 Final/Reese\Final.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        conn.close()
        print("Fetched data from SQLite:", rows)  # Verify the data is correct
        return rows
    except Exception as e:
        print(f"Error fetching data from SQLite: {e}")

fetch_data_from_sqlite()

