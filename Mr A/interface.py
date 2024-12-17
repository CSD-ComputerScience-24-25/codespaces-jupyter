import sqlite3, os
running = True
program_state = 'Main'

def clear_console():
    # Check the operating system and execute the appropriate command
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux, macOS, etc.
        os.system('clear')

while running:

    while program_state == 'Main':

        print("Mr A's Grocery Store")
        print('1) Process Transactions')
        print('2) Manage Inventory')
        print('3) View Transaction History')
        user_input = input("Select an option or type Done to exit.")

        if user_input == '1':
            program_state = 'Transaction Mode'
        elif user_input == '2':
            program_state = 'Inventory Mode'
        elif user_input == '3':
            program_state = 'Audit Mode'
        elif user_input == 'Done':
            program_state = 'Done'
            running = False

    while program_state == 'Transaction Mode':
        clear_console()
        print("Transaction Mode")
        print('1) Process Transactions')
        print('2) Manage Inventory')
        print('3) View Transaction History')
        user_input = input("Select an option or type Done to exit.")

        if user_input == '1':
            program_state = 'Transaction Mode'
        elif user_input == '2':
            program_state = 'Inventory Mode'
        elif user_input == '3':
            program_state = 'Audit Mode'
        elif user_input == 'Done':
            program_state = 'Done'
            running = False

conn = sqlite3.connect('My_db')
cur = conn.cursor()

cur.executemany('INSERT INTO Food (item_name, item_barcode, item_cost, item_total) VALUES ("Banana", 123456, '3.50', 5)',
                'INSERT INTO Food (item_name, item_barcode, item_cost, item_total) VALUES ("Banana", 123456, '3.50', 5)')

