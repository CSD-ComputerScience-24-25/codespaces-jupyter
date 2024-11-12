import sqlite3

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

while True:

    command = input ('enter an SQlite command')

    if command== "Done":
        cur.close()
        break 
    elif command.startswith('SELECT'):
        print(cur.fetchall(command))
    else :
        cur.execute(command)

conn.commit()

