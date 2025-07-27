from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get('Body', '').lower()
    print(f"Mensaje recibido: {incoming_msg}")  # Para verificar en logs

    response = MessagingResponse()
    response.message("Hola 👋, gracias por tu mensaje.")
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
