from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)
ADMIN_NUMBER = "whatsapp:+573222522564"
DB_PATH = "votes.db"

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT UNIQUE,
            opcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Registrar voto si no existe
def registrar_voto(telefono, opcion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO votos (telefono, opcion) VALUES (?, ?)", (telefono, opcion))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

# Obtener resultados actuales
def obtener_resultados():
    votos = {"Jhonata Díaz": 73, "Orlando Rayo": 29}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT opcion, COUNT(*) FROM votos GROUP BY opcion")
    for opcion, cantidad in c.fetchall():
        if opcion in votos:
            votos[opcion] += cantidad
        else:
            votos[opcion] = cantidad
    conn.close()
    return votos

# Reiniciar votos (sin tocar los votos fijos)
def reiniciar_encuesta():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM votos")
    conn.commit()
    conn.close()

# Webhook de WhatsApp
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    from_number = request.values.get('From')
    body = request.values.get('Body').strip().lower()
    resp = MessagingResponse()

    if body in ["hola", "hi", "buenas", "start"]:
        mensaje = (
            "📊 *Si las elecciones para elegir representante fueran mañana, ¿por quién votaría usted?*\n\n"
            "1️⃣ Jhonata Díaz\n"
            "2️⃣ Orlando Rayo\n\n"
            "Responda con 1 o 2 para emitir su voto."
        )
        resp.message(mensaje)

    elif body == "1":
        if registrar_voto(from_number, "Jhonata Díaz"):
            votos = obtener_resultados()
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            mensaje = (
                "✅ Gracias por votar por *Jhonata Díaz*.\n\n"
                "📊 *Resultados preliminares:*\n"
                f"🗳️ Jhonata Díaz: {votos.get('Jhonata Díaz', 73)} votos\n"
                f"🗳️ Orlando Rayo: {votos.get('Orlando Rayo', 29)} votos\n"
                f"🕒 Fecha y hora: {fecha}"
            )
        else:
            mensaje = "⚠️ Ya has votado. Solo se permite un voto por persona."
        resp.message(mensaje)

    elif body == "2":
        if registrar_voto(from_number, "Orlando Rayo"):
            votos = obtener_resultados()
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            mensaje = (
                "✅ Gracias por votar por *Orlando Rayo*.\n\n"
                "📊 *Resultados preliminares:*\n"
                f"🗳️ Jhonata Díaz: {votos.get('Jhonata Díaz', 73)} votos\n"
                f"🗳️ Orlando Rayo: {votos.get('Orlando Rayo', 29)} votos\n"
                f"🕒 Fecha y hora: {fecha}"
            )
        else:
            mensaje = "⚠️ Ya has votado. Solo se permite un voto por persona."
        resp.message(mensaje)

    elif body == "resultados" and from_number == ADMIN_NUMBER:
        votos = obtener_resultados()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mensaje = (
            "📊 *Resultados actuales:*\n"
            f"🗳️ Jhonata Díaz: {votos.get('Jhonata Díaz', 73)} votos\n"
            f"🗳️ Orlando Rayo: {votos.get('Orlando Rayo', 29)} votos\n"
            f"🕒 Fecha y hora: {fecha}"
        )
        resp.message(mensaje)

    elif body == "reiniciar" and from_number == ADMIN_NUMBER:
        reiniciar_encuesta()
        resp.message("🔄 Todos los votos han sido eliminados. La encuesta ha sido reiniciada.")

    else:
        resp.message("❌ Opción no válida.\n\nResponda con:\n1 para *Jhonata Díaz*\n2 para *Orlando Rayo*\n\nO escriba 'hola' para comenzar.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
