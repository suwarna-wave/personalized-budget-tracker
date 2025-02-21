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
        """Initialize the Budget Tracker application."""
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("850x600")
        self.root.configure(bg="#dfe6e9")

        # Data storage
        self.data_dir = os.path.expanduser("~/.budget_tracker")
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_file = os.path.join(self.data_dir, "budget_data.json")
        self.budget_data = {"income": 0, "expenses": {}, "transactions": [], "split_names": []}
        self.load_data()

        # Categories and sources
        self.expense_categories = ["Food", "Rent", "Entertainment", "Utilities", "Other"]
        self.income_sources = ["Salary", "Freelance", "Gift", "Investment", "Other"]

        # Status variable
        self.status_var = tk.StringVar(value="Ready")  # Initialized here

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("radiance")
        self.style.configure("TButton", font=("Helvetica", 12, "bold"), padding=6, relief="raised")
        self.style.configure("Action.TButton", background="#00b894", foreground="#ffffff")
        self.style.map("Action.TButton", background=[("active", "#00a676")], foreground=[("active", "#ffffff")])
        self.style.configure("TLabel", font=("Helvetica", 11), background="#dfe6e9", foreground="#2d3436")
        self.style.configure("TFrame", background="#dfe6e9")
        self.style.configure("TLabelframe", background="#dfe6e9", foreground="#2d3436")
        self.style.configure("TLabelframe.Label", font=("Helvetica", 13, "bold"), foreground="#2d3436")

        self.create_gui()

    def create_gui(self):
        """Create a compact and visually appealing GUI."""
        # Header
        header_frame = ttk.Frame(self.root, relief="raised", borderwidth=2)
        header_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(header_frame, text="Personal Budget Tracker", font=("Helvetica", 22, "bold"), foreground="#2d3436").pack(pady=10)

        # Main content frame
        main_frame = ttk.Frame(self.root, relief="groove", borderwidth=2)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left panel for inputs
        input_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        input_frame.pack(side="left", fill="y", padx=10, pady=5)
        income_btn = ttk.Button(input_frame, text="Add Income", command=lambda: self.add_transaction("Income"), style="Action.TButton")
        income_btn.pack(pady=10, fill="x")
        expense_btn = ttk.Button(input_frame, text="Add Expense", command=lambda: self.add_transaction("Expense"), style="Action.TButton")
        expense_btn.pack(pady=10, fill="x")

        # Right panel for history
        history_frame = ttk.LabelFrame(main_frame, text="History", padding=10)
        history_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)
        self.history_text = tk.Text(history_frame, height=20, width=50, font=("Helvetica", 10), bg="#ffffff", fg="#2d3436", relief="flat", borderwidth=1)
        self.history_text.pack(fill="both", expand=True)
        self.update_history()

        # Bottom buttons frame
        buttons_frame = ttk.Frame(self.root, relief="groove", borderwidth=2)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        button_specs = [
            ("Summary", self.show_summary, "View financial summary"),
            ("Chart", self.show_chart, "Show expense distribution"),
            ("Monthly", self.show_monthly_summary, "View monthly breakdown"),
            ("PDF", self.download_pdf, "Export to PDF"),
            ("CSV", self.download_csv, "Export to CSV")
        ]
        for text, command, tip in button_specs:
            btn = ttk.Button(buttons_frame, text=text, command=command)
            btn.pack(side="left", padx=5, pady=5)
            self.create_tooltip(btn, tip)

        # Status bar
        status_bar = ttk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 10), background="#b2bec3", relief="sunken", anchor="w")
        status_bar.pack(fill="x", padx=10, pady=2)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        label = ttk.Label(tooltip, text=text, background="#f1c40f", foreground="#2d3436", padding=3, relief="solid", borderwidth=1)
        label.pack()
        tooltip.withdraw()

        def show(event):
            x, y = event.x_root + 10, event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def hide(event):
            tooltip.withdraw()

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    def add_transaction(self, type_):
        """Open a compact transaction entry window."""
        window = tk.Toplevel(self.root)
        window.title(f"Add {type_}")
        window.geometry("400x450")
        window.configure(bg="#dfe6e9")
        window.transient(self.root)
        window.grab_set()

        style = ttk.Style(window)
        style.theme_use("radiance")
        style.configure("TLabel", background="#dfe6e9", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 12, "bold"), padding=6)

        form_frame = ttk.Frame(window, padding=15)
        form_frame.pack(fill="both", expand=True)

        if type_ == "Income":
            ttk.Label(form_frame, text="Income Amount:", font=("Helvetica", 13, "bold")).pack(pady=(5, 2))
            amount_entry = ttk.Entry(form_frame, font=("Helvetica", 11))
            amount_entry.pack(fill="x", pady=5)

            ttk.Label(form_frame, text="Source:", font=("Helvetica", 13, "bold")).pack(pady=(5, 2))
            source_var = tk.StringVar(value=self.income_sources[0])
            source_menu = ttk.Combobox(form_frame, textvariable=source_var, values=self.income_sources, font=("Helvetica", 11))
            source_menu.pack(fill="x", pady=5)

            ttk.Label(form_frame, text="Description (Optional):", font=("Helvetica", 13, "bold")).pack(pady=(5, 2))
            desc_entry = ttk.Entry(form_frame, font=("Helvetica", 11))
            desc_entry.pack(fill="x", pady=5)

            save_command = lambda: self.save_transaction(type_, amount_entry.get(), source_var.get(), None, desc_entry.get(), False, window)

        else:
            ttk.Label(form_frame, text="Expense Amount:", font=("Helvetica", 13, "bold")).pack(pady=(5, 2))
            amount_entry = ttk.Entry(form_frame, font=("Helvetica", 11))
            amount_entry.pack(fill="x", pady=5)

            ttk.Label(form_frame, text="Category:", font=("Helvetica", 13, "bold")).pack(pady=(5, 2))
            category_var = tk.StringVar(value=self.expense_categories[0])
            category_menu = ttk.Combobox(form_frame, textvariable=category_var, values=self.expense_categories, font=("Helvetica", 11))
            category_menu.pack(fill="x", pady=5)

            title_entry = ttk.Entry(form_frame, font=("Helvetica", 11))
            desc_entry = ttk.Entry(form_frame, font=("Helvetica", 11))

            def on_category_change(event):
                if category_var.get() == "Other":
                    ttk.Label(form_frame, text="Custom Title:", font=("Helvetica", 11)).pack(pady=(5, 2))
                    title_entry.pack(fill="x", pady=5)
                    ttk.Label(form_frame, text="Description (Optional):", font=("Helvetica", 11)).pack(pady=(5, 2))
                    desc_entry.pack(fill="x", pady=5)
                else:
                    for widget in form_frame.winfo_children():
                        if widget not in [amount_entry, category_menu] and widget.winfo_class() in ["TEntry", "TLabel"]:
                            widget.pack_forget()

            category_menu.bind("<<ComboboxSelected>>", on_category_change)

            ttk.Label(form_frame, text="Split?", font=("Helvetica", 13, "bold")).pack(pady=(5, 2))
            split_var = tk.BooleanVar()
            ttk.Checkbutton(form_frame, variable=split_var, command=lambda: self.handle_split(form_frame, split_var)).pack(pady=5)
            self.split_entries = []

            save_command = lambda: self.save_transaction(type_, amount_entry.get(), category_var.get(), title_entry.get(), desc_entry.get(), split_var.get(), window)

        ttk.Button(form_frame, text="Save", command=save_command).pack(pady=15)

        window.update_idletasks()
        width, height = window.winfo_width(), window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def handle_split(self, frame, split_var):
        """Handle split transaction input."""
        if split_var.get():
            ttk.Label(frame, text="Split Names:", font=("Helvetica", 11)).pack(pady=(5, 2))
            split_entry = ttk.Entry(frame, font=("Helvetica", 11))
            split_entry.pack(fill="x", pady=5)
            self.split_entries.append(split_entry)
        else:
            for entry in self.split_entries:
                entry.pack_forget()
            self.split_entries = []

    def save_transaction(self, type_, amount, category_or_source, title, desc, split, window):
        """Save the transaction and update status."""
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError(f"{type_} must be positive!")
            
            title = title if type_ == "Expense" and category_or_source == "Other" and title else category_or_source
            desc = desc if desc else "N/A"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            transaction = f"{timestamp} - {type_}: ${amount:.2f} - {title} - {desc}"

            if type_ == "Income":
                self.budget_data["income"] += amount
            else:
                self.budget_data["expenses"][title] = self.budget_data["expenses"].get(title, 0) + amount

            if type_ == "Expense" and split and self.split_entries:
                names = self.split_entries[0].get().split(",")
                self.budget_data["split_names"].extend([name.strip() for name in names if name.strip() and name.strip() not in self.budget_data["split_names"]])
                transaction += f" (Split: {', '.join(names)})"

            self.budget_data["transactions"].append(transaction)
            self.save_data()
            self.update_history()
            self.status_var.set(f"{type_} added successfully!")
            messagebox.showinfo("Success", f"{type_} added!", parent=self.root)
            window.destroy()
        except ValueError as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e) or "Invalid amount!", parent=window)

    def show_summary(self):
        """Display financial summary."""
        total_expenses = sum(self.budget_data["expenses"].values())
        balance = self.budget_data["income"] - total_expenses
        summary = f"Income: ${self.budget_data['income']:.2f}\nExpenses: ${total_expenses:.2f}\nBalance: ${balance:.2f}"
        self.status_var.set("Viewing summary")
        messagebox.showinfo("Summary", summary, parent=self.root)

    def show_chart(self):
        """Show expense pie chart."""
        if not self.budget_data["expenses"]:
            self.status_var.set("No expenses to chart")
            messagebox.showwarning("Warning", "No expenses to display!", parent=self.root)
            return
        plt.pie(self.budget_data["expenses"].values(), labels=self.budget_data["expenses"].keys(), autopct="%1.1f%%", colors=plt.cm.Paired.colors)
        plt.title("Expense Distribution", fontsize=14, fontweight="bold")
        self.status_var.set("Displaying expense chart")
        plt.show()

    def show_monthly_summary(self):
        """Display monthly summary with chart."""
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
            self.status_var.set("No transactions for monthly summary")
            messagebox.showinfo("Monthly Summary", "No transactions yet.", parent=self.root)
            return

        window = tk.Toplevel(self.root)
        window.title("Monthly Summary")
        window.geometry("600x500")
        window.configure(bg="#dfe6e9")

        text = tk.Text(window, height=10, width=60, font=("Helvetica", 10), bg="#ffffff", fg="#2d3436", relief="flat", borderwidth=1)
        text.pack(pady=10, padx=15)
        for month, data in monthly_data.items():
            total_expenses = sum(data["expenses"].values())
            text.insert(tk.END, f"{month}: Income: ${data['income']:.2f} | Expenses: ${total_expenses:.2f} | Balance: ${data['income'] - total_expenses:.2f}\n")

        latest_month = max(monthly_data.keys())
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.pie(monthly_data[latest_month]["expenses"].values(), labels=monthly_data[latest_month]["expenses"].keys(), autopct="%1.1f%%", colors=plt.cm.Paired.colors)
        ax.set_title(f"Spending for {latest_month}", fontsize=12, fontweight="bold")
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=15)
        self.status_var.set("Showing monthly summary")

    def download_pdf(self):
        """Export transactions to PDF."""
        try:
            filename = f"budget_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0, 0.72, 0.58)
            c.drawCentredString(300, 750, "Personal Budget Tracker Report")
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0, 0, 0)
            y = 720
            for trans in self.budget_data["transactions"]:
                c.drawString(40, y, trans)
                y -= 15
                if y < 40:
                    c.showPage()
                    y = 750
            c.save()
            self.status_var.set(f"PDF saved: {filename}")
            messagebox.showinfo("Success", f"PDF saved as {filename}", parent=self.root)
        except Exception as e:
            self.status_var.set(f"PDF export failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}", parent=self.root)

    def download_csv(self):
        """Export transactions to CSV."""
        try:
            filename = f"budget_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Type", "Amount", "Title/Source", "Description", "Splits"])
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
            self.status_var.set(f"CSV saved: {filename}")
            messagebox.showinfo("Success", f"CSV saved as {filename}", parent=self.root)
        except Exception as e:
            self.status_var.set(f"CSV export failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to save CSV: {str(e)}", parent=self.root)

    def update_history(self):
        """Update transaction history display."""
        self.history_text.delete("1.0", tk.END)
        for trans in self.budget_data["transactions"]:
            self.history_text.insert(tk.END, trans + "\n")
        self.status_var.set(f"History updated: {len(self.budget_data['transactions'])} entries")

    def save_data(self):
        """Save data to JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.budget_data, f)

    def load_data(self):
        """Load data from JSON file."""
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