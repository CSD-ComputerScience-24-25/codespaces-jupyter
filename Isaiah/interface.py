import sqlite3, os
running = True
program_state = "Main"
while running:
    while program_state == "Main":
        print("What would you like to do")
        print("1: Manage Inventory")
        print("2: Process transactions")
        print("3: Admin mode:o")
        rahh = input("select what you want to do(by number): ")

        if rahh == "1":
            program_state = "Inventory Managing"
        elif rahh == "2":
            program_state = "Transactions processed"
        elif rahh == "3":
            program_state = "The legendary Admin mode!!"
        elif rahh == "Done":
            program_state = "Main"
            running = False
    while program_state == "Invetory Managing":
        print("Inventory Mode")
        print("1: View inventory")
        print("2: Add to inventory")
        print("3: Remove from inventory")
        print("4: Update inventory")










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