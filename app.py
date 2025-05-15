from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

# If you have any blueprints or other modules, import them here
import twilio_webhook  # 

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Make sure this is set!

# ... all your route code like /login, /dashboard, /logout, etc ...

@app.route('/')
def home():
    return redirect('/login')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

