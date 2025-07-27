from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Número autorizado como administrador (cambia este número al tuyo de Twilio o personal)
ADMIN_NUMBER = "whatsapp:+573222522564"

DB_PATH = "votes.db"

# Inicializar base de datos
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

# Registrar voto si no ha votado antes
def registrar_voto(telefono, opcion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO votos (telefono, opcion) VALUES (?, ?)", (telefono, opcion))
        conn.commit()
        registrado = True
    except sqlite3.IntegrityError:
        registrado = False
    conn.close()
    return registrado

# Obtener conteo actual de votos
def obtener_resultados():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT opcion, COUNT(*) FROM votos GROUP BY opcion")
    votos_bd = dict(c.fetchall())
    conn.close()
    # Resultados con base
    jhonatan = 73 + votos_bd.get("Jhonata Díaz", 0)
    orlando = 29 + votos_bd.get("Orlando Rayo", 0)
    return jhonatan, orlando

# Reiniciar encuesta (solo admin)
def reiniciar_encuesta():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM votos")
    conn.commit()
    conn.close()

# Webhook de Twilio para recibir mensajes
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    from_number = request.values.get("From")
    body = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()

    if body in ["hola", "hi", "buenas", "start"]:
        resp.message(
            "📊 Si las elecciones para elegir representante fueran mañana, ¿por quién votaría usted?\n\n"
            "1️⃣ Jhonata Díaz\n"
            "2️⃣ Orlando Rayo\n\n"
            "Responde con 1 o 2."
        )
    
    elif body in ["1", "2"]:
        opcion = "Jhonata Díaz" if body == "1" else "Orlando Rayo"
        exito = registrar_voto(from_number, opcion)
        if exito:
            j, o = obtener_resultados()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resp.message(
                f"✅ Tu voto por *{opcion}* ha sido registrado. ¡Gracias por participar!\n\n"
                f"📈 Resultados preliminares:\n"
                f"🟢 Jhonata Díaz: {j} votos\n"
                f"🔵 Orlando Rayo: {o} votos\n\n"
                f"🕒 Fecha y hora: {fecha}"
            )
        else:
            resp.message("❌ Ya has votado anteriormente. Solo se permite un voto por número.")
    
    elif body == "resultados" and from_number == ADMIN_NUMBER:
        j, o = obtener_resultados()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resp.message(
            f"📊 Resultados actuales:\n\n"
            f"🟢 Jhonata Díaz: {j} votos\n"
            f"🔵 Orlando Rayo: {o} votos\n\n"
            f"🕒 Fecha y hora: {fecha}"
        )

    elif body == "reiniciar" and from_number == ADMIN_NUMBER:
        reiniciar_encuesta()
        resp.message("🔄 La encuesta ha sido reiniciada correctamente.")

    else:
        resp.message(
            "❌ Opción no válida.\n\n"
            "📊 Si las elecciones para elegir representante fueran mañana, ¿por quién votaría usted?\n"
            "1️⃣ Jhonata Díaz\n"
            "2️⃣ Orlando Rayo\n\n"
            "Responde con 1 o 2."
        )

    return str(resp)

# Ejecutar app localmente o en un servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
