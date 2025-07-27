from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)

ADMIN_NUMBER = "whatsapp:+573222522564"
DB_PATH = "votes.db"

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT,
            opcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Registrar voto
def registrar_voto(telefono, opcion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO votos (telefono, opcion) VALUES (?, ?)", (telefono, opcion))
    conn.commit()
    conn.close()

# Obtener resultados totales incluyendo votos fijos
def obtener_resultados():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT opcion, COUNT(*) FROM votos GROUP BY opcion")
    votos = {"Jhonata Díaz": 73, "Orlando Rayo": 29}
    for opcion, cantidad in c.fetchall():
        if opcion in votos:
            votos[opcion] += cantidad
        else:
            votos[opcion] = cantidad
    conn.close()
    return votos

# Reiniciar votos
def reiniciar_encuesta():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM votos")
    conn.commit()
    conn.close()

# Webhook principal
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    from_number = request.values.get('From')
    body = request.values.get('Body').strip().lower()
    resp = MessagingResponse()

    if body in ["hola", "hi", "buenas", "start"]:
        resp.message("👋 ¡Hola! ¿Por quién quieres votar?\n\n1️⃣ Jhonata Díaz\n2️⃣ Orlando Rayo\n\nResponde con 1 o 2.")

    elif body == "1":
        registrar_voto(from_number, "Jhonata Díaz")
        votos = obtener_resultados()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mensaje = (
            "✅ Tu voto por *Jhonata Díaz* ha sido registrado. ¡Gracias!\n\n"
            "📊 Resultados actuales:\n"
            f"Jhonata Díaz: {votos.get('Jhonata Díaz', 73)} votos\n"
            f"Orlando Rayo: {votos.get('Orlando Rayo', 29)} votos\n"
            f"🕒 Fecha y hora: {fecha}"
        )
        resp.message(mensaje)

    elif body == "2":
        registrar_voto(from_number, "Orlando Rayo")
        votos = obtener_resultados()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mensaje = (
            "✅ Tu voto por *Orlando Rayo* ha sido registrado. ¡Gracias!\n\n"
            "📊 Resultados actuales:\n"
            f"Jhonata Díaz: {votos.get('Jhonata Díaz', 73)} votos\n"
            f"Orlando Rayo: {votos.get('Orlando Rayo', 29)} votos\n"
            f"🕒 Fecha y hora: {fecha}"
        )
        resp.message(mensaje)

    elif body == "resultados" and from_number == ADMIN_NUMBER:
        votos = obtener_resultados()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mensaje = (
            "📊 Resultados actuales:\n"
            f"Jhonata Díaz: {votos.get('Jhonata Díaz', 73)} votos\n"
            f"Orlando Rayo: {votos.get('Orlando Rayo', 29)} votos\n"
            f"🕒 Fecha y hora: {fecha}"
        )
        resp.message(mensaje)

    elif body == "reiniciar" and from_number == ADMIN_NUMBER:
        reiniciar_encuesta()
        resp.message("🔄 La encuesta ha sido reiniciada correctamente (votos manuales conservados).")

    else:
        resp.message("❌ Opción no válida.\nResponde con:\n1 para *Jhonata Díaz*\n2 para *Orlando Rayo*\n\nO escribe 'hola' para empezar.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
