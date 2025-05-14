import sqlite3

# Connect to the database
conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

# Ask for new restaurant details
name = input("Enter restaurant name (e.g. Pizza Palace): ")
username = input("Enter restaurant username (e.g. pizzapalace): ")
password = input("Enter restaurant password: ")

# Insert into the restaurants table
cursor.execute("""
INSERT INTO restaurants (name, username, password)
VALUES (?, ?, ?)
""", (name, username, password))

conn.commit()
conn.close()

print(f"Restaurant '{name}' added successfully.")
