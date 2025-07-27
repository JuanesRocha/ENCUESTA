from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp funcionando ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").lower()
    print("Mensaje recibido:", incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    # Lógica de respuesta básica
    if "hola" in incoming_msg:
        msg.body("¡Hola! ¿Cómo estás?")
    elif "gracias" in incoming_msg:
        msg.body("¡Con gusto! 😊")
    else:
        msg.body("No entendí tu mensaje. Escribe 'hola' para comenzar.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
