import sqlite3

#conn = sqlite3.connect('Reese\Reese.sqlite')
conn = sqlite3.connect('Reese\MRA_Users.sqlite')
cur = conn.cursor()

while True:

    try:
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
    except:
        print("Command Failed") 