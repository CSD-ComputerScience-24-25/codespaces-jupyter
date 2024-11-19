import sqlite3

db = "MRA_Users.sqlite"
conn = sqlite3.connect(db)
cur = conn.cursor()

while True:

    command = input('Enter an SQLite Command: ')

    if command == 'Done':
        cur.close()
        break
    elif command.startswith("SELECT"):
        cur.execute(command)
        for item in cur.fetchall():
            print(item)
    else:
        cur.execute(command)
    

conn.commit()

"""SELECT User.name, Role.title, Course.title
  FROM User JOIN Member JOIN Course JOIN Role
  ON Member.user_id = User.id AND Member.course_id = Course.id AND Member.role = Role.id
  ORDER BY Course.title, Role.id DESC, User.name """
