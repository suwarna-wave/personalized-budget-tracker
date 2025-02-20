

# Personal Budget Tracker

**A sleek, user-friendly desktop application to manage your finances with style and precision.**

Welcome to the **Personal Budget Tracker**, a Python-based tool designed to help you track income, expenses, and spending patterns effortlessly. Built with a modern GUI, this application offers intuitive transaction management, data visualization, and export options, making it perfect for personal finance enthusiasts and a standout addition to your portfolio.

---

## ✨ Features

- **Modern GUI**: Crafted with `ttkthemes` for a professional, visually appealing interface.
- **Income & Expense Tracking**: Add transactions with categories, custom titles, descriptions, and optional splits.
- **Transaction History**: View all entries in a clean, scrollable list.
- **Data Visualization**: Generate pie charts for overall and monthly expense breakdowns.
- **Export Options**: Download reports as PDF or CSV files with a single click.
- **Persistent Storage**: Saves data to a JSON file in your user directory (`~/.budget_tracker`).
- **User-Friendly**: Transaction windows close automatically after saving, with clear error handling.

---

## 📸 Screenshots

| Main Window | Add Transaction | Monthly Summary |
|-------------|-----------------|-----------------|
| ![Main Window](https://via.placeholder.com/300x200.png?text=Main+Window) | ![Add Transaction](https://via.placeholder.com/300x200.png?text=Add+Transaction) | ![Monthly Summary](https://via.placeholder.com/300x200.png?text=Monthly+Summary) |

*Replace placeholders with actual screenshots by capturing your app and uploading them to GitHub.*

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**: Ensure Python is installed on your system.
- **pip**: Python package manager (comes with Python).

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/personal-budget-tracker.git
   cd personal-budget-tracker
   ```

2. **Install Dependencies**:
   ```bash
   pip install matplotlib reportlab ttkthemes
   ```
   - `matplotlib`: For pie charts.
   - `reportlab`: For PDF generation.
   - `ttkthemes`: For the modern GUI theme.

3. **Run the Application**:
   ```bash
   python budget_tracker.py
   ```

---

## 🛠️ Usage

1. **Launch the App**:
   - Run the script to open the main window.

2. **Add Transactions**:
   - Click **Add Income** or **Add Expense**.
   - Enter an amount, select a category (or "Other" for custom title/description), and optionally split the transaction.
   - Hit **Save** to record and close the window.

3. **View Insights**:
   - **Show Summary**: Displays total income, expenses, and balance.
   - **Spending Chart**: Visualizes overall expense distribution.
   - **Monthly Summary**: Shows monthly breakdowns with a chart for the latest month.

4. **Export Data**:
   - **Download PDF**: Saves a formatted report.
   - **Download CSV**: Exports transaction details for spreadsheets.

5. **Data Persistence**:
   - Transactions are saved to `~/.budget_tracker/budget_data.json`.

---

## 📋 File Structure

```
personal-budget-tracker/
│
├── budget_tracker.py      # Main application script
├── README.md              # This file
├── .gitignore             # Git ignore file (optional)
└── budget_data.json       # Generated data file (in ~/.budget_tracker/)
```

---

## 🔧 Dependencies

| Library       | Version  | Purpose                  |
|---------------|----------|--------------------------|
| `matplotlib`  | Latest   | Data visualization       |
| `reportlab`   | Latest   | PDF generation           |
| `ttkthemes`   | Latest   | Modern GUI themes        |
| `tkinter`     | Built-in | GUI framework            |
| `json`        | Built-in | Data persistence         |
| `csv`         | Built-in | CSV export               |

---

## 💡 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

---

## 🐛 Troubleshooting

- **ModuleNotFoundError**: Ensure all dependencies are installed (`pip install matplotlib reportlab ttkthemes`).
- **File Access Errors**: Check write permissions in `~/.budget_tracker/`.
- **GUI Not Displaying**: Verify Python and Tkinter are installed correctly (`python -m tkinter`).

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (create one if desired).

---

## 🌟 Acknowledgements

- Built with ❤️ using Python and Tkinter.
- Inspired by personal finance management needs.
- Thanks to the open-source community for amazing libraries!

---

**Happy Budgeting!**  
For questions or suggestions, open an issue or reach out at [your.email@example.com](mailto:suwarnapyakurel5@example.com).



