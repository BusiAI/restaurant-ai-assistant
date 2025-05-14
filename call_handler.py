from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai
import sqlite3

app = Flask(__name__)
openai.api_key = "sk-...xV8A"

def save_order(restaurant_id, order_text):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (restaurant_id, order_text) VALUES (?, ?)", (restaurant_id, order_text))
    conn.commit()
    conn.close()

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()

    # Step 1: Greet the customer
    response.say("Hi, thanks for calling Burger Place. What would you like to order today?", voice="Polly.Brian")  # UK accent

    # Step 2: Gather input
    response.record(maxLength=10, action="/process", method="POST")

    return str(response)

@app.route("/process", methods=["POST"])
def process():
    response = VoiceResponse()
    recording_url = request.form["RecordingUrl"]

    # Step 3: Get transcript from audio (mocked for now)
    # You’ll replace this with real transcription later
    fake_order = "One cheeseburger with fries and a coke"

    # Step 4: Save to database under Burger Place (assume ID 3)
    save_order(3, fake_order)

    response.say("Thanks! Your order has been placed. Goodbye!", voice="Polly.Brian")
    response.hangup()

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

