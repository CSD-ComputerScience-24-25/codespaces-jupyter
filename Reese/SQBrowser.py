import sqlite3

#conn = sqlite3.connect('Reese\Reese.sqlite')
conn = sqlite3.connect('/workspaces/codespaces-jupyter/Reese/Semester 1 Final/Groccery-Store-SQLite-DB-Reese.sqlite')
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
        
## SELECT User.name, Role.title, Course.title FROM User JOIN Member JOIN Course JOIN Role ON Member.user_id = User.id AND Member.course_id = Course.id AND Member.role = Role.id ORDER BY Course.title, Role.id DESC, User.name