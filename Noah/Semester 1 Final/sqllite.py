import sqlite3

#database
db = ('crane.sqlite')

conn = sqlite3.connect(db)

cursor = conn.cursor()

while True : 

    command = input ('enter command: ')

    if command == "Done" :
        cursor.close()
        break
    elif command.startswith("SELECT"):
        cursor.execute(command)
        for thing in cursor.fetchall():
            print(thing)
    else :

        cursor.execute(command)

conn.commit()