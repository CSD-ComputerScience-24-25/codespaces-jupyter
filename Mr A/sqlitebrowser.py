import sqlite3

conn = sqlite3.connect('Mr.A\db.sqlite')
cur = conn.cursor()

while True:

    command = input('Enter an SQLite Command: ')

    if command == 'Done':
        cur.close()
        break
    elif command.startswith("SELECT"):
        cur.execute(command)
        print(cur.fetchall())
    else:
        cur.execute(command)
    

conn.commit()
