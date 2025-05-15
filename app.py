from flask import Flask, request, render_template, redirect, session, url_for
from twilio.twiml.voice_response import VoiceResponse
import sqlite3
import openai
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Load OpenAI API Key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# ====== DATABASE SETUP ======
def get_db_connection():
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    return conn

# ====== LOGIN SYSTEM ======
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        restaurant_name = request.form["restaurant"]
        password = request.form["password"]

        conn = get_db_connection()
        restaurant = conn.execute("SELECT * FROM restaurants WHERE name = ? AND password = ?", (restaurant_name, password)).fetchone()
        conn.close()

        if restaurant:
            session["restaurant"] = restaurant_name
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "restaurant" not in session:
        return redirect("/login")

    restaurant = session["restaurant"]
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders WHERE restaurant = ? ORDER BY id DESC", (restaurant,)).fetchall()
    conn.close()
    return render_template("dashboard.html", restaurant=restaurant, orders=orders)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    return redirect("/login")

# ====== TWILIO WEBHOOK ======
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()

    caller = request.form.get("From", "Unknown")
    transcript = request.form.get("SpeechResult", "")

    # Prompt design for AI
    prompt = f"""You are taking an order for a restaurant. The user said: '{transcript}'.
Respond clearly, and ask for delivery or collection, then confirm the address or order.
If they mention allergies, be cautious. Only confirm the order after clarifying everything."""

    try:
        ai_result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a friendly phone assistant taking food orders."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_response = ai_result["choices"][0]["message"]["content"]
    except Exception as e:
        ai_response = "Sorry, there was an error processing your order. Please try again later."

    # Store to database
    conn = get_db_connection()
    conn.execute("INSERT INTO orders (restaurant, customer_number, order_text) VALUES (?, ?, ?)",
                 ("Pizza Palace", caller, transcript + " | " + ai_response))
    conn.commit()
    conn.close()

    response.say(ai_response)
    response.hangup()
    return str(response)

# ====== RENDER/PRODUCTION ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
