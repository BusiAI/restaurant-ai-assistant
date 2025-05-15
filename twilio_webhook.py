# twilio_webhook.py
from flask import request, Response
from twilio.twiml.voice_response import VoiceResponse

from app import app  # Import the existing app

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()

    prompt = "This is Pizza Palace. Please place your order after the beep. You can ask questions about the menu or let us know if you have allergies."

    # Simulated AI response (replace with actual OpenAI logic later)
    ai_response = "Thank you! Your margherita pizza and garlic bread will be ready for pickup in 20 minutes."

    response.say(prompt)
    response.pause(length=3)
    response.say(ai_response)
    response.hangup()

    return Response(str(response), mimetype="application/xml")
