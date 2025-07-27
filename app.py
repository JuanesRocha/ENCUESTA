from flask import Flask, request, send_file
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Número de administrador autorizado (cambia este al tuyo real de Twilio)
ADMIN_NUMBER = "whatsapp:+573001234567"  # reemplaza con tu número

DB_PATH = "votes.db"

# Inicializar DB
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

# Guardar voto
def registrar_voto(telefono, opcion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO votos (telefono, opcion) VALUES (?, ?)", (telefono, opcion))
    conn.commit()
    conn.close()

# Obtener resultados
def obtener_resultados():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT opcion, COUNT(*) as votos FROM votos GROUP BY opcion", conn)
    conn.close()
    return df

# Vaciar tabla de votos
def reiniciar_encuesta():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM votos")
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp funcionando ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.form
    numero = data.get("From")
    mensaje = data.get("Body", "").strip().lower()

    resp = MessagingResponse()
    mensaje_respuesta = ""

    if mensaje in ["hola", "inicio", "empezar"]:
        mensaje_respuesta = (
            "👋 ¡Hola! ¿Por quién quieres votar?\n\n"
            "1️⃣ Jhonata Díaz\n"
            "2️⃣ Orlando Rayo\n\n"
            "Escribe: *1* o *2* para registrar tu voto."
        )

    elif mensaje == "1":
        registrar_voto(numero, "Jhonata Díaz")
        mensaje_respuesta = "✅ Tu voto por *Jhonata Díaz* ha sido registrado."

    elif mensaje == "2":
        registrar_voto(numero, "Orlando Rayo")
        mensaje_respuesta = "✅ Tu voto por *Orlando Rayo* ha sido registrado."

    elif mensaje == "resultados" and numero == ADMIN_NUMBER:
        df = obtener_resultados()
        if df.empty:
            mensaje_respuesta = "No hay votos registrados todavía."
        else:
            resultados_texto = "\n".join(
                [f"🗳️ {row['opcion']}: {row['votos']} votos" for _, row in df.iterrows()]
            )
            mensaje_respuesta = f"📊 Resultados actuales:\n\n{resultados_texto}"

            # Generar Excel
            excel_path = "resultados_encuesta.xlsx"
            df.to_excel(excel_path, index=False)

    elif mensaje == "reiadm" and numero == ADMIN_NUMBER:
        reiniciar_encuesta()
        mensaje_respuesta = "🔁 Encuesta reiniciada correctamente."

    else:
        mensaje_respuesta = "❓ No entendí tu mensaje. Escribe 'Hola' para comenzar."

    resp.message(mensaje_respuesta)
    return str(resp), 200

@app.route("/descargar_resultados", methods=["GET"])
def descargar_resultados():
    if os.path.exists("resultados_encuesta.xlsx"):
        return send_file("resultados_encuesta.xlsx", as_attachment=True)
    else:
        return "No se ha generado aún el archivo de resultados.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
