import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
from datetime import datetime
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ttkthemes import ThemedTk

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        self.data_dir = os.path.expanduser("~/.budget_tracker")
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_file = os.path.join(self.data_dir, "budget_data.json")
        self.budget_data = {"income": 0, "expenses": {}, "transactions": [], "split_names": []}
        self.load_data()

        self.categories = ["Food", "Rent", "Entertainment", "Utilities", "Other"]

        self.style = ttk.Style()
        self.style.theme_use("radiance")
        self.style.configure("TButton", font=("Helvetica", 12), padding=5)
        self.style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabelframe.Label", font=("Helvetica", 14, "bold"), foreground="#333333")

        self.create_gui()

    def create_gui(self):
        title_label = ttk.Label(self.root, text="Personal Budget Tracker", font=("Helvetica", 24, "bold"), foreground="#2c3e50")
        title_label.pack(pady=15)

        main_frame = ttk.Frame(self.root, relief="groove", borderwidth=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        input_frame = ttk.LabelFrame(main_frame, text="Add Transaction", padding=10)
        input_frame.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Button(input_frame, text="Add Income", command=lambda: self.add_transaction("Income")).pack(pady=10, fill="x")
        ttk.Button(input_frame, text="Add Expense", command=lambda: self.add_transaction("Expense")).pack(pady=10, fill="x")

        history_frame = ttk.LabelFrame(main_frame, text="Transaction History", padding=10)
        history_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.history_text = tk.Text(history_frame, height=20, width=50, font=("Helvetica", 10), bg="#ffffff", fg="#333333", relief="flat", borderwidth=1)
        self.history_text.pack(fill="both", expand=True)
        self.update_history()

        buttons_frame = ttk.Frame(self.root, relief="groove", borderwidth=2)
        buttons_frame.pack(pady=15, fill="x", padx=20)
        buttons = [
            ("Show Summary", self.show_summary),
            ("Spending Chart", self.show_chart),
            ("Monthly Summary", self.show_monthly_summary),
            ("Download PDF", self.download_pdf),
            ("Download CSV", self.download_csv)
        ]
        for text, command in buttons:
            ttk.Button(buttons_frame, text=text, command=command).pack(side="left", padx=10, pady=5)

    def add_transaction(self, type_):
        window = tk.Toplevel(self.root)
        window.title(f"Add {type_}")
        window.geometry("400x500")
        window.configure(bg="#f0f0f0")

        style = ttk.Style(window)
        style.theme_use("radiance")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12), padding=5)

        ttk.Label(window, text=f"{type_} Amount:", font=("Helvetica", 14, "bold"), foreground="#2c3e50").pack(pady=10)
        amount_entry = ttk.Entry(window, font=("Helvetica", 12))
        amount_entry.pack(pady=5, padx=20, fill="x")

        ttk.Label(window, text="Category/Title:", font=("Helvetica", 14, "bold"), foreground="#2c3e50").pack(pady=10)
        category_var = tk.StringVar(value=self.categories[0])
        category_menu = ttk.Combobox(window, textvariable=category_var, values=self.categories, font=("Helvetica", 12))
        category_menu.pack(pady=5, padx=20, fill="x")

        title_entry = ttk.Entry(window, font=("Helvetica", 12))
        desc_entry = ttk.Entry(window, font=("Helvetica", 12))

        def on_category_change(event):
            if category_var.get() == "Other":
                ttk.Label(window, text="Custom Title:", font=("Helvetica", 12)).pack(pady=5)
                title_entry.pack(pady=5, padx=20, fill="x")
                ttk.Label(window, text="Description (Optional):", font=("Helvetica", 12)).pack(pady=5)
                desc_entry.pack(pady=5, padx=20, fill="x")
            else:
                for widget in window.winfo_children():
                    if widget not in [amount_entry, category_menu] and widget.winfo_class() in ["TEntry", "TLabel"]:
                        widget.pack_forget()

        category_menu.bind("<<ComboboxSelected>>", on_category_change)

        ttk.Label(window, text="Split Transaction?", font=("Helvetica", 14, "bold"), foreground="#2c3e50").pack(pady=10)
        split_var = tk.BooleanVar()
        ttk.Checkbutton(window, variable=split_var, command=lambda: self.handle_split(window, split_var)).pack(pady=5)
        self.split_entries = []

        ttk.Button(window, text="Save", command=lambda: self.save_transaction(type_, amount_entry.get(), category_var.get(), title_entry.get(), desc_entry.get(), split_var.get(), window)).pack(pady=20)

        window.update_idletasks()
        width, height = window.winfo_width(), window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def handle_split(self, window, split_var):
        if split_var.get():
            ttk.Label(window, text="Split Names (comma-separated):", font=("Helvetica", 12)).pack(pady=5)
            split_entry = ttk.Entry(window, font=("Helvetica", 12))
            split_entry.pack(pady=5, padx=20, fill="x")
            self.split_entries.append(split_entry)
        else:
            for entry in self.split_entries:
                entry.pack_forget()
            self.split_entries = []

    def save_transaction(self, type_, amount, category, title, desc, split, window):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError(f"{type_} must be positive!")
            title = title if category == "Other" and title else category
            desc = desc if desc else "No description"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            transaction = f"{timestamp} - {type_}: ${amount:.2f} - {title} - {desc}"
            
            if type_ == "Income":
                self.budget_data["income"] += amount
            else:
                self.budget_data["expenses"][title] = self.budget_data["expenses"].get(title, 0) + amount
            
            if split and self.split_entries:
                names = self.split_entries[0].get().split(",")
                self.budget_data["split_names"].extend([name.strip() for name in names if name.strip() and name.strip() not in self.budget_data["split_names"]])
                transaction += f" (Split: {', '.join(names)})"
            
            self.budget_data["transactions"].append(transaction)
            self.save_data()
            self.update_history()
            messagebox.showinfo("Success", f"{type_} added!", parent=self.root)
            window.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e) or "Invalid amount!", parent=window)

    def show_summary(self):
        total_expenses = sum(self.budget_data["expenses"].values())
        balance = self.budget_data["income"] - total_expenses
        summary = f"Total Income: ${self.budget_data['income']:.2f}\nTotal Expenses: ${total_expenses:.2f}\nBalance: ${balance:.2f}"
        messagebox.showinfo("Summary", summary, parent=self.root)

    def show_chart(self):
        if not self.budget_data["expenses"]:
            messagebox.showwarning("Warning", "No expenses to display!", parent=self.root)
            return
        plt.pie(self.budget_data["expenses"].values(), labels=self.budget_data["expenses"].keys(), autopct="%1.1f%%", colors=plt.cm.Paired.colors)
        plt.title("Expense Distribution")
        plt.show()

    def show_monthly_summary(self):
        monthly_data = {}
        for trans in self.budget_data["transactions"]:
            date, rest = trans.split(" - ", 1)
            month = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
            if month not in monthly_data:
                monthly_data[month] = {"income": 0, "expenses": {}}
            if "Income" in rest:
                amount = float(rest.split("$")[1].split(" - ")[0])
                monthly_data[month]["income"] += amount
            else:
                amount = float(rest.split("$")[1].split(" - ")[0])
                category = rest.split(" - ")[1]
                monthly_data[month]["expenses"][category] = monthly_data[month]["expenses"].get(category, 0) + amount

        if not monthly_data:
            messagebox.showinfo("Monthly Summary", "No transactions yet.", parent=self.root)
            return

        window = tk.Toplevel(self.root)
        window.title("Monthly Summary")
        window.geometry("600x500")
        window.configure(bg="#f0f0f0")

        text = tk.Text(window, height=10, width=70, font=("Helvetica", 10), bg="#ffffff", fg="#333333", relief="flat", borderwidth=1)
        text.pack(pady=10, padx=20)
        for month, data in monthly_data.items():
            total_expenses = sum(data["expenses"].values())
            text.insert(tk.END, f"{month}: Income: ${data['income']:.2f}, Expenses: ${total_expenses:.2f}, Balance: ${data['income'] - total_expenses:.2f}\n")

        latest_month = max(monthly_data.keys())
        fig, ax = plt.subplots()
        ax.pie(monthly_data[latest_month]["expenses"].values(), labels=monthly_data[latest_month]["expenses"].keys(), autopct="%1.1f%%", colors=plt.cm.Paired.colors)
        ax.set_title(f"Spending for {latest_month}")
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=20)

    def download_pdf(self):
        try:
            filename = f"budget_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0.1, 0.2, 0.3)
            c.drawString(100, 750, "Personal Budget Tracker Report")
            c.setFillColorRGB(0, 0, 0)
            y = 700
            for trans in self.budget_data["transactions"]:
                c.drawString(100, y, trans)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            messagebox.showinfo("Success", f"PDF saved as {filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}", parent=self.root)

    def download_csv(self):
        try:
            filename = f"budget_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Type", "Amount", "Title", "Description", "Splits"])
                for trans in self.budget_data["transactions"]:
                    parts = trans.split(" - ")
                    type_amount = parts[1].split(": $")
                    type_ = type_amount[0]
                    amount = type_amount[1].split(" - ")[0]
                    title = parts[2]
                    desc_splits = parts[3].split(" (Split: ")
                    desc = desc_splits[0]
                    splits = desc_splits[1][:-1] if len(desc_splits) > 1 else ""
                    writer.writerow([parts[0], type_, amount, title, desc, splits])
            messagebox.showinfo("Success", f"CSV saved as {filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {str(e)}", parent=self.root)

    def update_history(self):
        self.history_text.delete("1.0", tk.END)
        for trans in self.budget_data["transactions"]:
            self.history_text.insert(tk.END, trans + "\n")

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.budget_data, f)

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.budget_data = json.load(f)
        except FileNotFoundError:
            self.budget_data = {"income": 0, "expenses": {}, "transactions": [], "split_names": []}

if __name__ == "__main__":
    try:
        root = ThemedTk(theme="radiance")
        app = BudgetTracker(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("Application closed by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")