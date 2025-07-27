from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot WhatsApp funcionando."

@app.route("/webhook", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender = request.values.get('From')

    print(f"Mensaje de {sender}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "hola":
        msg.body("👋 ¡Hola! Soy un bot de prueba. Escribe cualquier cosa y te responderé.")
    else:
        msg.body(f"Recibí tu mensaje: '{incoming_msg}' 🙌")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
