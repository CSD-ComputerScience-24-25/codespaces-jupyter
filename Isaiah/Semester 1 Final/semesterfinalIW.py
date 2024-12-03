import sqlite3

db = "WEBBstore.sqlite"
conn = sqlite3.connect(db)
cur = conn.cursor

while True:
    command = input("Enter an sqlite command: ")
    if command == "Done":
        cur.close
        break
    elif command.startswith("SELECT"):
        cur.execute(command)
        print(cur.fetchall()[0])
    else:
        cur.execute(command)

conn.commit()