from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'Bot de WhatsApp funcionando ✅'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Mensaje recibido:", data)
    # Aquí puedes procesar el mensaje recibido y responder usando Twilio
    return 'OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

