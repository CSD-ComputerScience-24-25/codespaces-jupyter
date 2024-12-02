### **Project Description: Grocery Store Inventory Application**
In this project, students will create a Python application that simulates a grocery store inventory management system. The application will run in the terminal and allow users to perform the following functions:  

1. **Manage Inventory**:
   - Add new items to the inventory.
   - Update details of existing items (e.g., price, quantity).
   - Delete items from the inventory.

2. **Process Transactions**:
   - Record sales and purchases.
   - Update the inventory quantities accordingly.

3. **Query the Database**:
   - Display all inventory items with their details.
   - Generate reports, such as total sales or inventory worth.

The program must use SQLite to store and retrieve inventory and transaction data. Students should implement a user-friendly menu system to navigate through the application features.

---

### **Requirements**
- Use Python and SQLite for the application.
- Create an `inventory` table to store item details (e.g., item ID, name, price, quantity).
- Create a `transactions` table to record sales and purchase transactions (e.g., transaction ID, item ID, type of transaction, quantity, date).
- Provide a terminal interface with clear options for all required functionalities.
- Implement error handling to manage invalid inputs (e.g., non-existent item IDs or incorrect data formats).

---

### **Scoring Rubric (50 Points Total)**

| **Category**                  | **Criteria**                                                                 | **Points** |
|--------------------------------|------------------------------------------------------------------------------|------------|
| **Database Design (10 pts)**  | - Includes properly structured `inventory` and `transactions` tables.        | 5 pts      |
|                                | - Uses appropriate data types for columns (e.g., INTEGER for IDs, REAL for prices). | 5 pts      |
| **Functionality (20 pts)**    | - Allows adding, updating, and deleting inventory items.                     | 8 pts      |
|                                | - Records and retrieves transactions correctly.                              | 8 pts      |
|                                | - Updates inventory quantities based on transactions.                        | 4 pts      |
| **User Interface (10 pts)**   | - Provides a clear, user-friendly menu system.                               | 5 pts      |
|                                | - Handles invalid inputs gracefully.                                        | 5 pts      |
| **Code Quality (5 pts)**      | - Follows good coding practices (e.g., clear variable names, comments).      | 3 pts      |
|                                | - Demonstrates logical structure and organization of code.                  | 2 pts      |
| **Creativity (5 pts)**        | - Adds at least one innovative or extra feature (e.g., data export, filtering). | 5 pts      |

---

