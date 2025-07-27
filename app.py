from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "")
    print(f"Mensaje de whatsapp:{request.form.get('From')}: {incoming_msg}")

    # Creamos la respuesta
    resp = MessagingResponse()
    resp.message("Hola 👋, gracias por tu mensaje.")
    
    return str(resp), 200  # 👈 Importante: retornar correctamente

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
