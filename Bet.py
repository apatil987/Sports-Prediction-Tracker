import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Bet class to store information about each bet
class Bet:
    def __init__(self, sport, amount, odds, outcome, bet_type):
        self.sport = sport
        self.amount = float(amount)
        self.odds = float(odds)
        self.outcome = outcome
        self.bet_type = bet_type

# SQLite database connection
conn = sqlite3.connect('bets.db')
cursor = conn.cursor()

# Create a table to store bets if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sport TEXT,
        amount REAL,
        odds REAL,
        outcome TEXT,
        bet_type TEXT
    )
''')
conn.commit()

# Function to add a bet to the database
def save_bet_to_db(bet):
    cursor.execute("INSERT INTO bets (sport, amount, odds, outcome, bet_type) VALUES (?, ?, ?, ?, ?)",
                   (bet.sport, bet.amount, bet.odds, bet.outcome, bet.bet_type))
    conn.commit()

# Function to add a bet
def add_bet():
    sport = sport_var.get()
    amount = amount_entry.get()
    odds = odds_entry.get()
    outcome = outcome_var.get()
    bet_type = bet_type_var.get()
    
    if not sport or not amount or not odds or not outcome or not bet_type:
        messagebox.showerror("Error", "All fields must be filled in!")
        return
    
    try:
        bet = Bet(sport, amount, odds, outcome, bet_type)
        save_bet_to_db(bet)
        messagebox.showinfo("Bet Added", f"Added {bet_type} bet on {sport}")
        clear_entries()
    except ValueError:
        messagebox.showerror("Error", "Invalid input! Please enter numbers for Amount and Odds.")

# Clear entry fields
def clear_entries():
    sport_var.set("Football")  # Reset dropdown to default value
    amount_entry.delete(0, tk.END)
    odds_entry.delete(0, tk.END)

# Function to display statistics
def show_stats():
    cursor.execute("SELECT * FROM bets")
    bets = cursor.fetchall()

    if not bets:
        messagebox.showinfo("Stats", "No bets to show.")
        return
    
    total_wins = sum((row[2] * row[3]) - row[2] for row in bets if row[4] == "Win")
    total_losses = sum(row[2] for row in bets if row[4] == "Loss")
    net_profit = total_wins - total_losses
    win_percentage = (len([row for row in bets if row[4] == "Win"]) / len(bets)) * 100 if bets else 0
    
    stats = f"Total Wins: ${total_wins:.2f}\nTotal Losses: ${total_losses:.2f}\nNet Profit/Loss: ${net_profit:.2f}\nWin Percentage: {win_percentage:.2f}%"
    messagebox.showinfo("Stats", stats)

# Function to generate a graph using Pandas and Matplotlib
def show_graph():
    # Read data from SQLite database using Pandas
    df = pd.read_sql_query("SELECT * FROM bets", conn)
    
    if df.empty:
        messagebox.showinfo("No Data", "No data to display.")
        return

    # Create a bar graph showing total bet amounts by bet type
    bet_type_totals = df.groupby('bet_type')['amount'].sum()

    bet_type_totals.plot(kind='bar', color='skyblue')
    plt.title("Total Bet Amount by Bet Type")
    plt.xlabel("Bet Type")
    plt.ylabel("Total Amount ($)")
    plt.show()

# Function to clear all data from the database
def clear_all_bets():
    response = messagebox.askyesno("Confirm", "Are you sure you want to clear all bet data?")
    if response:
        cursor.execute("DELETE FROM bets")
        conn.commit()
        messagebox.showinfo("Cleared", "All bet data has been cleared.")

# Function to show all previous wagers
def show_wager_history():
    cursor.execute("SELECT * FROM bets")
    wagers = cursor.fetchall()

    if not wagers:
        messagebox.showinfo("No Wagers", "No wagers to display.")
        return
    
    # Create a new window to show wagers
    history_window = tk.Toplevel(root)
    history_window.title("Wager History")
    
    # Create a Treeview widget to display the wagers in table format
    tree = ttk.Treeview(history_window, columns=("Sport", "Amount", "Odds", "Outcome", "Bet Type"), show='headings')
    tree.heading("Sport", text="Sport")
    tree.heading("Amount", text="Amount")
    tree.heading("Odds", text="Odds")
    tree.heading("Outcome", text="Outcome")
    tree.heading("Bet Type", text="Bet Type")
    
    tree.grid(row=0, column=0, sticky='nsew')

    # Add a scrollbar
    scrollbar = tk.Scrollbar(history_window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    # Insert wagers into the Treeview
    for wager in wagers:
        tree.insert("", "end", values=(wager[1], wager[2], wager[3], wager[4], wager[5]))

# Create main window
root = tk.Tk()
root.title("Event Outcome Tracker")

# Dropdown for Sport selection
tk.Label(root, text="Sport:").grid(row=0, column=0)
sport_var = tk.StringVar(root)
sport_var.set("Football")  # Default value

sport_dropdown = tk.OptionMenu(root, sport_var, "Football", "Basketball", "Hockey", "Baseball")
sport_dropdown.grid(row=0, column=1)

# Input fields for amount, odds, outcome, and bet type
tk.Label(root, text="Amount:").grid(row=1, column=0)
amount_entry = tk.Entry(root)
amount_entry.grid(row=1, column=1)

tk.Label(root, text="Odds:").grid(row=2, column=0)
odds_entry = tk.Entry(root)
odds_entry.grid(row=2, column=1)

tk.Label(root, text="Outcome:").grid(row=3, column=0)
outcome_var = tk.StringVar()
tk.Radiobutton(root, text="Win", variable=outcome_var, value="Win").grid(row=3, column=1)
tk.Radiobutton(root, text="Loss", variable=outcome_var, value="Loss").grid(row=3, column=2)

# Dropdown for Bet Type
tk.Label(root, text="Bet Type:").grid(row=4, column=0)
bet_type_var = tk.StringVar(root)
bet_type_var.set("Moneyline")  # Default value

bet_type_menu = tk.OptionMenu(root, bet_type_var, "Moneyline", "Total", "Spread")
bet_type_menu.grid(row=4, column=1)

# Add buttons
tk.Button(root, text="Add Bet", command=add_bet).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="Show Stats", command=show_stats).grid(row=6, column=0, columnspan=2)
tk.Button(root, text="Show Graph", command=show_graph).grid(row=7, column=0, columnspan=2)
tk.Button(root, text="Clear All Bets", command=clear_all_bets).grid(row=8, column=0, columnspan=2)
tk.Button(root, text="Show Wager History", command=show_wager_history).grid(row=9, column=0, columnspan=2)

root.mainloop()

# Close the database connection when the app is closed
conn.close()