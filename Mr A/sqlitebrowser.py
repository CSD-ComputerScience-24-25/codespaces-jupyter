import sqlite3

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

while True:

    command = input('Enter an SQLite Command: ')

    if command == 'Done':
        cur.close()
        break
    elif command.startswith("SELECT"):
        print(cur.fetchall())
    else:
        cur.execute(command)
    

    conn.commit()
