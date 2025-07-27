from flask import Flask, request, send_file
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Número de administrador autorizado
ADMIN_NUMBER = "whatsapp:+573222522564"  # Reemplaza por tu número de Twilio o personal

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

# Guardar voto
def registrar_voto(telefono, opcion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO votos (telefono, opcion) VALUES (?, ?)", (telefono, opcion))
    conn.commit()
    conn.close()

# Obtener resultados en DataFrame
def obtener_resultados():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT opcion, COUNT(*) as votos FROM votos GROUP BY opcion", conn)
    conn.close()
    return df

# Reiniciar la encuesta
def reiniciar_encuesta():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM votos")
    conn.commit()
    conn.close()

# Ruta principal
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot de WhatsApp funcionando correctamente."

# Webhook de WhatsApp
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    from_number = request.values.get('From')
    body = request.values.get('Body').strip().lower()

    print("Mensaje recibido desde:", from_number)
    print("Contenido:", body)

    resp = MessagingResponse()

    # Comandos principales
    if body in ["hola", "hi", "buenas", "start"]:
        resp.message("👋 ¡Hola! ¿Por quién quieres votar?\n\n1️⃣ Jhonata Díaz\n2️⃣ Orlando Rayo\n\nResponde con 1 o 2.")
    
    elif body == "1":
        registrar_voto(from_number, "Jhonata Díaz")
        resp.message("✅ Tu voto por *Jhonata Díaz* ha sido registrado. ¡Gracias!")
    
    elif body == "2":
        registrar_voto(from_number, "Orlando Rayo")
        resp.message("✅ Tu voto por *Orlando Rayo* ha sido registrado. ¡Gracias!")

    elif body == "resultados" and from_number == ADMIN_NUMBER:
        df = obtener_resultados()
        if df.empty:
            mensaje = "📭 No hay votos aún."
        else:
            mensaje = "📊 Resultados actuales:\n\n"
            for _, row in df.iterrows():
                mensaje += f"{row['opcion']}: {row['votos']} votos\n"
            # También se guarda archivo
            df.to_excel("resultados_encuesta.xlsx", index=False)
        resp.message(mensaje)

    elif body == "reiniciar" and from_number == ADMIN_NUMBER:
        reiniciar_encuesta()
        resp.message("🔄 La encuesta ha sido reiniciada correctamente.")

    else:
        resp.message("❌ Opción no válida.\nResponde con:\n1 para *Jhonata Díaz*\n2 para *Orlando Rayo*\n\nO escribe 'hola' para empezar.")

    return str(resp)

# Descargar resultados desde navegador
@app.route("/descargar_resultados", methods=["GET"])
def descargar_resultados():
    if os.path.exists("resultados_encuesta.xlsx"):
        return send_file("resultados_encuesta.xlsx", as_attachment=True)
    else:
        return "❌ No se ha generado aún el archivo de resultados.", 404

# Ejecutar app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
