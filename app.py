from flask import Flask, request, render_template, redirect, session
from twilio.twiml.voice_response import VoiceResponse
import sqlite3
import openai
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")


# Load OpenAI API Key from environment
openai.api_key = os.getenv("sk-...xV8A")

# ====== DATABASE CONNECTION ======
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
        restaurant = conn.execute(
            "SELECT * FROM restaurants WHERE name = ? AND password = ?",
            (restaurant_name, password)
        ).fetchone()
        conn.close()

        if restaurant:
            session["restaurant"] = restaurant_name
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ====== DASHBOARD ======
@app.route("/dashboard")
def dashboard():
    if "restaurant" not in session:
        return redirect("/login")

    restaurant = session["restaurant"]
    conn = get_db_connection()
    orders = conn.execute(
        "SELECT * FROM orders WHERE restaurant = ? ORDER BY id DESC",
        (restaurant,)
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", restaurant=restaurant, orders=orders)

# ====== LOGOUT ======
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    return redirect("/login")

# ====== TWILIO VOICE WEBHOOK ======
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()

    caller = request.form.get("From", "Unknown")
    transcript = request.form.get("SpeechResult", "")

    prompt = f"""You are taking an order for a restaurant. The customer said: '{transcript}'.
Respond clearly, ask if they want delivery or collection, and confirm details. Mention allergies if needed."""

    try:
        ai_result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful food ordering assistant."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_response = ai_result["choices"][0]["message"]["content"]
    except Exception:
        ai_response = "Sorry, there was a problem. Please call again shortly."

    # Save order
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO orders (restaurant, customer_number, order_text) VALUES (?, ?, ?)",
        ("Pizza Palace", caller, transcript + " | " + ai_response)
    )
    conn.commit()
    conn.close()

    response.say(ai_response)
    response.hangup()
    return str(response)

# ====== RENDER DEPLOYMENT ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
