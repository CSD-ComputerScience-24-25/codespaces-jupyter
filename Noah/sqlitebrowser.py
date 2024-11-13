import sqlite3

db = "RIP.sqlite"
conn = sqlite3.connect(db)
cur = conn.cursor()

while True:

    command = input ('enter an SQlite command: ')

    if command== "Done":
        cur.close()
        break 
    elif command.startswith("SELECT"):
        cur.execute(command)
        print(cur.fetchall())
    else :
        cur.execute(command)

conn.commit()

