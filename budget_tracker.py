import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime
import os

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("600x700")

        # Data storage
        self.data_dir = os.path.expanduser("~/.budget_tracker")
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_file = os.path.join(self.data_dir, "budget_data.json")
        self.budget_data = {"income": 0, "expenses": {}, "transactions": []}
        self.load_data()

        # Categories
        self.categories = ["Food", "Rent", "Entertainment", "Utilities", "Other"]

        # GUI
        self.create_gui()

    def create_gui(self):
        # Title
        tk.Label(self.root, text="Personal Budget Tracker", font=("Arial", 20, "bold")).pack(pady=10)

        # Income Frame
        income_frame = ttk.Frame(self.root)
        income_frame.pack(pady=10, padx=10, fill="x")
        ttk.Label(income_frame, text="Income:").pack(side="left", padx=5)
        self.income_entry = ttk.Entry(income_frame)
        self.income_entry.pack(side="left", padx=5)
        ttk.Button(income_frame, text="Add Income", command=self.add_income).pack(side="left", padx=5)

        # Expense Frame
        expense_frame = ttk.Frame(self.root)
        expense_frame.pack(pady=10, padx=10, fill="x")
        ttk.Label(expense_frame, text="Expense Amount:").pack(side="left", padx=5)
        self.expense_entry = ttk.Entry(expense_frame)
        self.expense_entry.pack(side="left", padx=5)
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_menu = ttk.Combobox(expense_frame, textvariable=self.category_var, values=self.categories)
        self.category_menu.pack(side="left", padx=5)
        ttk.Button(expense_frame, text="Add Expense", command=self.add_expense).pack(side="left", padx=5)

        # Buttons Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Show Summary", command=self.show_summary).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Spending Chart", command=self.show_chart).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Monthly Summary", command=self.show_monthly_summary).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Clear Data", command=self.clear_data).pack(side="left", padx=10)

        # Transaction History
        ttk.Label(self.root, text="Transaction History", font=("Arial", 14)).pack(pady=5)
        self.history_text = tk.Text(self.root, height=15, width=70)
        self.history_text.pack(pady=5)
        self.update_history()

    def add_income(self):
        try:
            income = float(self.income_entry.get())
            if income <= 0:
                raise ValueError("Income must be positive!")
            self.budget_data["income"] += income
            self.budget_data["transactions"].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Income: +${income:.2f}")
            self.save_data()
            self.update_history()
            messagebox.showinfo("Success", f"Added ${income:.2f} to income!")
            self.income_entry.delete(0, tk.END)
            self.check_balance()
        except ValueError as e:
            messagebox.showerror("Error", str(e) if str(e) else "Please enter a valid number!")

    def add_expense(self):
        try:
            amount = float(self.expense_entry.get())
            if amount <= 0:
                raise ValueError("Expense must be positive!")
            category = self.category_var.get()
            self.budget_data["expenses"][category] = self.budget_data["expenses"].get(category, 0) + amount
            self.budget_data["transactions"].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {category}: -${amount:.2f}")
            self.save_data()
            self.update_history()
            messagebox.showinfo("Success", f"Added ${amount:.2f} to {category}!")
            self.expense_entry.delete(0, tk.END)
            self.check_balance()
        except ValueError as e:
            messagebox.showerror("Error", str(e) if str(e) else "Please enter a valid number!")

    def show_summary(self):
        total_expenses = sum(self.budget_data["expenses"].values())
        balance = self.budget_data["income"] - total_expenses
        summary = f"Total Income: ${self.budget_data['income']:.2f}\n"
        summary += f"Total Expenses: ${total_expenses:.2f}\n"
        summary += f"Remaining Balance: ${balance:.2f}"
        messagebox.showinfo("Budget Summary", summary)

    def show_chart(self):
        if not self.budget_data["expenses"]:
            messagebox.showwarning("Warning", "No expenses to display!")
            return
        categories = list(self.budget_data["expenses"].keys())
        amounts = list(self.budget_data["expenses"].values())
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
        plt.title("Spending Distribution")
        plt.axis("equal")
        plt.show()

    def show_monthly_summary(self):
        monthly_data = {}
        for trans in self.budget_data["transactions"]:
            date, desc = trans.split(" - ", 1)
            month = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
            if month not in monthly_data:
                monthly_data[month] = {"income": 0, "expenses": {}}
            if "Income" in desc:
                amount = float(desc.split("$")[1])
                monthly_data[month]["income"] += amount
            else:
                category, amount = desc.split(": -$", 1)
                amount = float(amount)
                monthly_data[month]["expenses"][category] = monthly_data[month]["expenses"].get(category, 0) + amount

        if not monthly_data:
            messagebox.showinfo("Monthly Summary", "No transactions yet.")
            return

        # Monthly Summary Window
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Monthly Summary")
        summary_window.geometry("600x500")

        summary_text = tk.Text(summary_window, height=10, width=70)
        summary_text.pack(pady=10)
        for month, data in monthly_data.items():
            total_expenses = sum(data["expenses"].values())
            balance = data["income"] - total_expenses
            summary_text.insert(tk.END, f"{month}: Income: ${data['income']:.2f}, Expenses: ${total_expenses:.2f}, Balance: ${balance:.2f}\n")

        # Pie Chart for Latest Month
        latest_month = max(monthly_data.keys())
        expenses = monthly_data[latest_month]["expenses"]
        if expenses:
            fig, ax = plt.subplots()
            ax.pie(expenses.values(), labels=expenses.keys(), autopct="%1.1f%%", startangle=90)
            ax.set_title(f"Spending for {latest_month}")
            ax.axis("equal")
            canvas = FigureCanvasTkAgg(fig, master=summary_window)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

    def clear_data(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            self.budget_data = {"income": 0, "expenses": {}, "transactions": []}
            self.save_data()
            self.update_history()
            messagebox.showinfo("Success", "Data cleared!")

    def check_balance(self):
        total_expenses = sum(self.budget_data["expenses"].values())
        if total_expenses > self.budget_data["income"]:
            messagebox.showwarning("Warning", "Expenses exceed income!")

    def update_history(self):
        self.history_text.delete("1.0", tk.END)
        for transaction in self.budget_data["transactions"]:
            self.history_text.insert(tk.END, transaction + "\n")

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.budget_data, f)

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.budget_data = json.load(f)
        except FileNotFoundError:
            self.budget_data = {"income": 0, "expenses": {}, "transactions": []}

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTracker(root)
    root.mainloop()