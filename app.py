from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot WhatsApp funcionando."

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "hola" in incoming_msg:
        msg.body("👋 ¡Hola! Soy tu bot en WhatsApp. ¿En qué puedo ayudarte?")
    else:
        msg.body("🤖 No entendí. Escribe 'hola' para comenzar.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
