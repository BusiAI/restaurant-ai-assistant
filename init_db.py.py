import sqlite3

# Connect to a new database file called 'orders.db'
conn = sqlite3.connect('orders.db')
c = conn.cursor()

# Create a table for restaurants
c.execute('''
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Create a table for orders
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    customer_name TEXT,
    items TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
)
''')

# Insert a test restaurant login (username: pizzauser, password: testpass)
c.execute('''
INSERT OR IGNORE INTO restaurants (name, username, password)
VALUES (?, ?, ?)
''', ('Pizza Palace', 'pizzauser', 'testpass'))

# Save changes and close the connection
conn.commit()
conn.close()
