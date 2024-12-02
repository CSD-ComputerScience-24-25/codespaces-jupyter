### **Tips for Building the Grocery Store Inventory Application**

Here are some tips to help you succeed in building your Python and SQLite project:

---

### **1. Plan Before You Code**
- **Understand the Requirements**:
  - Make a list of features you need to implement (e.g., adding items, updating inventory, recording transactions).
- **Design the Database**:
  - Think about what information each table should store.
  - Example:  
    - `inventory` table: `item_id`, `name`, `price`, `quantity`  
    - `transactions` table: `transaction_id`, `item_id`, `type`, `quantity`, `date`
- **Sketch the Menu System**:
  - Draft what your menu options will look like in the terminal.

---

### **2. Work Incrementally**
- Start with small, testable features:
  - Create the database and tables first.
  - Write a simple script to add a new item to the `inventory` table.
- Test each feature before moving to the next.

---

### **3. Master SQLite Basics**
- **Creating Tables**:
  ```sql
  CREATE TABLE inventory (
      item_id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      price REAL NOT NULL,
      quantity INTEGER NOT NULL
  );
  ```
- **Inserting Data**:
  ```python
  cursor.execute("INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?)", ("Apple", 0.50, 100))
  ```
- **Querying Data**:
  ```python
  cursor.execute("SELECT * FROM inventory")
  rows = cursor.fetchall()
  for row in rows:
      print(row)
  ```

---

### **4. Use Functions to Organize Code**
- Break down your code into reusable functions:
  ```python
  def add_item(cursor):
      name = input("Enter item name: ")
      price = float(input("Enter item price: "))
      quantity = int(input("Enter item quantity: "))
      cursor.execute("INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
  ```
- Write separate functions for each menu option (e.g., `update_item`, `delete_item`, `record_transaction`).

---

### **5. Handle Errors Gracefully**
- Use `try-except` blocks to manage errors:
  ```python
  try:
      quantity = int(input("Enter quantity: "))
  except ValueError:
      print("Please enter a valid number.")
  ```
- Check for invalid IDs before processing transactions:
  ```python
  cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
  item = cursor.fetchone()
  if item is None:
      print("Item not found.")
  ```

---

### **6. Use Libraries for Better User Input**
- Use the `tabulate` library to display data in a neat table:
  ```bash
  pip install tabulate
  ```
  ```python
  from tabulate import tabulate

  def display_inventory(cursor):
      cursor.execute("SELECT * FROM inventory")
      rows = cursor.fetchall()
      print(tabulate(rows, headers=["ID", "Name", "Price", "Quantity"], tablefmt="grid"))
  ```

---

### **7. Test Your Application**
- Test each feature independently:
  - Can you add, update, and delete items correctly?
  - Are transactions updating the inventory properly?
- Test edge cases:
  - What happens if you try to sell more items than are in stock?

---

### **8. Add Extra Features for Creativity**
- Export inventory or transactions to a CSV file:
  ```python
  import csv

  def export_inventory(cursor):
      cursor.execute("SELECT * FROM inventory")
      rows = cursor.fetchall()
      with open("inventory.csv", "w", newline="") as file:
          writer = csv.writer(file)
          writer.writerow(["ID", "Name", "Price", "Quantity"])
          writer.writerows(rows)
      print("Inventory exported to inventory.csv")
  ```
- Add filters for displaying inventory (e.g., show only low-stock items).

---

### **9. Resources to Help You**
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Python SQLite Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Tabulate Documentation](https://pypi.org/project/tabulate/)

---

### **10. Keep Your Code Readable**
- Use clear variable names and add comments:
  ```python
  # Update the price of an item
  def update_price(cursor, item_id, new_price):
      cursor.execute("UPDATE inventory SET price = ? WHERE item_id = ?", (new_price, item_id))
  ```

