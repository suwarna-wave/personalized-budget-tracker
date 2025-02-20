import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
import json
from datetime import datetime
import csv
from PIL import Image, ImageTk
import os

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("600x700")
        ctk.set_appearance_mode("dark")  # Default to dark
        ctk.set_default_color_theme("blue")

        # Data storage
        self.budget_data = {"income": 0, "expenses": {}, "transactions": []}
        self.load_data()

        # Predefined categories
        self.categories = ["Food", "Rent", "Entertainment", "Utilities", "Other"]

        # Splash Screen
        self.show_splash_screen()

        # GUI Elements
        self.create_gui()

    def show_splash_screen(self):
        splash = ctk.CTkToplevel(self.root)
        splash.geometry("300x200")
        splash.overrideredirect(True)  # No window border
        splash.attributes("-topmost", True)
        
        # Load and display an icon/image (create a simple budget_icon.png or use any image)
        try:
            img = Image.open("budget_icon.png")  # Replace with your image path
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            ctk.CTkLabel(splash, image=photo, text="").pack(pady=20)
        except FileNotFoundError:
            ctk.CTkLabel(splash, text="Loading...", font=("Arial", 20)).pack(pady=20)
        
        ctk.CTkLabel(splash, text="Personal Budget Tracker", font=("Arial", 16)).pack()
        splash.update()
        splash.after(2000, splash.destroy)  # Close after 2 seconds

    def create_gui(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Light Theme", command=lambda: self.set_theme("light"))
        settings_menu.add_command(label="Dark Theme", command=lambda: self.set_theme("dark"))
        settings_menu.add_command(label="Monthly Summary", command=self.show_monthly_summary)

        # Title with Icon
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(pady=10)
        try:
            img = Image.open("budget_icon.png").resize((30, 30), Image.Resampling.LANCZOS)
            self.icon = ImageTk.PhotoImage(img)
            ctk.CTkLabel(title_frame, image=self.icon, text="").pack(side="left", padx=5)
        except FileNotFoundError:
            pass
        ctk.CTkLabel(title_frame, text="Personal Budget Tracker", font=("Arial", 20, "bold")).pack(side="left")

        # Income Frame
        income_frame = ctk.CTkFrame(self.root)
        income_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(income_frame, text="Income:").pack(side="left", padx=5)
        self.income_entry = ctk.CTkEntry(income_frame, placeholder_text="Enter amount")
        self.income_entry.pack(side="left", padx=5)
        ctk.CTkButton(income_frame, text="Add Income", command=self.add_income).pack(side="left", padx=5)

        # Expense Frame
        expense_frame = ctk.CTkFrame(self.root)
        expense_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(expense_frame, text="Expense Amount:").pack(side="left", padx=5)
        self.expense_entry = ctk.CTkEntry(expense_frame, placeholder_text="Enter amount")
        self.expense_entry.pack(side="left", padx=5)
        self.category_var = ctk.StringVar(value=self.categories[0])
        self.category_menu = ctk.CTkOptionMenu(expense_frame, values=self.categories, variable=self.category_var)
        self.category_menu.pack(side="left", padx=5)
        ctk.CTkButton(expense_frame, text="Add Expense", command=self.add_expense).pack(side="left", padx=5)

        # Buttons Frame
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Show Summary", command=self.show_summary).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Spending Chart", command=self.show_chart).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Export to CSV", command=self.export_to_csv).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Clear Data", command=self.clear_data).pack(side="left", padx=10)

        # Transaction History
        self.history_label = ctk.CTkLabel(self.root, text="Transaction History", font=("Arial", 14))
        self.history_label.pack(pady=5)
        self.history_text = ctk.CTkTextbox(self.root, height=200, width=500)
        self.history_text.pack(pady=5)
        self.update_history()

    def set_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.root.update()

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

    def show_monthly_summary(self):
        monthly_data = {}
        for trans in self.budget_data["transactions"]:
            date, desc = trans.split(" - ", 1)
            month = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
            if month not in monthly_data:
                monthly_data[month] = {"income": 0, "expenses": 0}
            if "Income" in desc:
                amount = float(desc.split("$")[1])
                monthly_data[month]["income"] += amount
            else:
                amount = float(desc.split("$")[1])
                monthly_data[month]["expenses"] += amount
        
        summary = "Monthly Summary:\n\n"
        for month, data in monthly_data.items():
            balance = data["income"] - data["expenses"]
            summary += f"{month}: Income: ${data['income']:.2f}, Expenses: ${data['expenses']:.2f}, Balance: ${balance:.2f}\n"
        if not monthly_data:
            summary += "No transactions yet."
        messagebox.showinfo("Monthly Summary", summary)

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

    def export_to_csv(self):
        filename = f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Description"])
            writer.writerows([t.split(" - ", 1) for t in self.budget_data["transactions"]])
            writer.writerow(["Total Income", self.budget_data["income"]])
            writer.writerow(["Category", "Amount"])
            writer.writerows(self.budget_data["expenses"].items())
        messagebox.showinfo("Success", f"Data exported to {filename}!")

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
        with open("budget_data.json", "w") as f:
            json.dump(self.budget_data, f)

    def load_data(self):
        try:
            with open("budget_data.json", "r") as f:
                self.budget_data = json.load(f)
        except FileNotFoundError:
            self.budget_data = {"income": 0, "expenses": {}, "transactions": []}

if __name__ == "__main__":
    root = ctk.CTk()
    app = BudgetTracker(root)
    root.mainloop()