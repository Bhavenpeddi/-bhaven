import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Create or connect to the SQLite database
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Create the expenses table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    amount REAL NOT NULL,
    description TEXT,
    category TEXT,
    date TEXT
)
''')

# Functions to handle operations
def add_expense():
    try:
        amount = float(entry_amount.get())
        description = entry_description.get()
        category = combo_category.get()
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if amount <= 0 or not description or not category:
            messagebox.showwarning("Input Error", "Please fill in all fields with valid information.")
            return
        
        cursor.execute('''
        INSERT INTO expenses (amount, description, category, date)
        VALUES (?, ?, ?, ?)
        ''', (amount, description, category, date))
        conn.commit()

        messagebox.showinfo("Success", "Expense added successfully.")
        clear_fields()
        view_expenses()

    except ValueError:
        messagebox.showwarning("Input Error", "Amount must be a valid number.")

def view_expenses():
    # Clear the listbox before updating
    listbox_expenses.delete(0, tk.END)

    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    if expenses:
        for expense in expenses:
            listbox_expenses.insert(tk.END, f"ID: {expense[0]} | Amount: ${expense[1]} | {expense[2]} | {expense[3]} | Date: {expense[4]}")
    else:
        listbox_expenses.insert(tk.END, "No expenses found.")

def delete_expense():
    try:
        # Get the selected expense (ID, Amount, Description, Category, Date)
        selected_expense = listbox_expenses.curselection()

        if not selected_expense:
            messagebox.showwarning("Selection Error", "Please select an expense to delete.")
            return

        # Get the full text of the selected item
        selected_text = listbox_expenses.get(selected_expense)

        # Extract the expense ID from the selected item
        # Assuming the format is "ID: <id> | Amount: <amount> | Description: <description> | ..."
        expense_id = int(selected_text.split('|')[0].split(':')[1].strip())

        # Delete the selected expense from the database
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()

        # Show success message and refresh the expenses list
        messagebox.showinfo("Success", "Expense deleted successfully.")
        view_expenses()

    except IndexError:
        messagebox.showwarning("Selection Error", "Please select an expense to delete.")
    except ValueError:
        messagebox.showwarning("Error", "There was an issue with the selected expense.")


def calculate_total():
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total = cursor.fetchone()[0]
    total = total if total else 0
    label_total.config(text=f"Total Expenses: ${total:.2f}")

def clear_fields():
    entry_amount.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    combo_category.set("")

# Creating the main window
root = tk.Tk()
root.title("Expense Tracker")

# Create the GUI layout
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

label_amount = tk.Label(frame_input, text="Amount:")
label_amount.grid(row=0, column=0, padx=5, pady=5)

entry_amount = tk.Entry(frame_input)
entry_amount.grid(row=0, column=1, padx=5, pady=5)

label_description = tk.Label(frame_input, text="Description:")
label_description.grid(row=1, column=0, padx=5, pady=5)

entry_description = tk.Entry(frame_input)
entry_description.grid(row=1, column=1, padx=5, pady=5)

label_category = tk.Label(frame_input, text="Category:")
label_category.grid(row=2, column=0, padx=5, pady=5)

categories = ["Food", "Entertainment", "Transport", "Bills", "Others"]
combo_category = tk.StringVar(value=categories[0])
category_menu = tk.OptionMenu(frame_input, combo_category, *categories)
category_menu.grid(row=2, column=1, padx=5, pady=5)

button_add = tk.Button(frame_input, text="Add Expense", command=add_expense)
button_add.grid(row=3, column=0, columnspan=2, pady=10)

# Displaying the list of expenses
frame_list = tk.Frame(root)
frame_list.pack(pady=10)

label_expenses = tk.Label(frame_list, text="Expenses List:")
label_expenses.pack()

listbox_expenses = tk.Listbox(frame_list, width=50, height=10)
listbox_expenses.pack(padx=5, pady=5)

button_delete = tk.Button(root, text="Delete Selected Expense", command=delete_expense)
button_delete.pack(pady=5)

# Total Expenses label
label_total = tk.Label(root, text="Total Expenses: $0.00", font=("Arial", 14))
label_total.pack(pady=10)

# Buttons to refresh the list and calculate total
button_refresh = tk.Button(root, text="Refresh Expenses", command=view_expenses)
button_refresh.pack(pady=5)

button_total = tk.Button(root, text="Calculate Total", command=calculate_total)
button_total.pack(pady=5)

# Start by viewing the expenses
view_expenses()

# Run the Tkinter event loop
root.mainloop()

# Close the database connection when the program ends
conn.close()
