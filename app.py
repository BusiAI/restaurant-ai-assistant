from flask import Flask, render_template_string, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed to manage user sessions

# HTML Templates inside Python (no need to create HTML files)
login_page = '''
<h2>Restaurant Login</h2>
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <input type="submit" value="Login">
</form>
<p style="color:red;">{{ error }}</p>
'''

orders_page = '''
<h2>Welcome {{ restaurant_name }}!</h2>
<p><a href="/logout">Logout</a></p>
<h3>Your Orders:</h3>
<ul>
  {% for order in orders %}
    <li><strong>{{ order[2] }}</strong>: {{ order[3] }} ({{ order[4] }})</li>
  {% endfor %}
</ul>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        c.execute("SELECT * FROM restaurants WHERE username=? AND password=?", (username, password))
        restaurant = c.fetchone()
        conn.close()
        if restaurant:
            session['restaurant_id'] = restaurant[0]
            session['restaurant_name'] = restaurant[1]
            return redirect('/orders')
        else:
            error = "Invalid credentials. Try again."
    return render_template_string(login_page, error=error)

@app.route('/orders')
def orders():
    if 'restaurant_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE restaurant_id=?", (session['restaurant_id'],))
    orders = c.fetchall()
    conn.close()
    return render_template_string(orders_page, restaurant_name=session['restaurant_name'], orders=orders)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def home():
    return redirect('/login')

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get the PORT from environment (Render sets it)
    app.run(host="0.0.0.0", port=port)
