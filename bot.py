import os
import time
import logging
import requests
import psycopg
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not TOKEN or not DATABASE_URL:
    raise ValueError("ERRO: TELEGRAM_TOKEN e DATABASE_URL precisam estar configurados!")

URL_API = f"https://api.telegram.org/bot{TOKEN}"

def init_db():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS estatisticas (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        contador INT DEFAULT 1
                    );
                """)
                conn.commit()
        logging.info("Banco de dados conectado e tabela verificada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao conectar no banco de dados: {e}")

def enviar_mensagem(chat_id, texto):
    requests.post(f"{URL_API}/sendMessage", json={"chat_id": chat_id, "text": texto})

def processar_mensagens(updates):
    for update in updates:
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            user_name = msg["from"].get("first_name", "Amigo")
            texto = msg.get("text", "")

            if texto == "/start":
                enviar_mensagem(chat_id, f"Olá, {user_name}! O seu bot `@ArrieguaIA_bot` está rodando no Python 3.14 com Neon! 🚀")
            else:
                try:
                    with psycopg.connect(DATABASE_URL) as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT contador FROM estatisticas WHERE user_id = %s;", (user_id,))
                            resultado = cursor.fetchone()
                            
                            if resultado:
                                novo_contador = resultado[0] + 1
                                cursor.execute("UPDATE estatisticas SET contador = %s WHERE user_id = %s;", (novo_contador, user_id))
                            else:
                                novo_contador = 1
                                cursor.execute("INSERT INTO estatisticas (user_id, contador) VALUES (%s, %s);", (user_id, novo_contador))
                                
                            conn.commit()
                    enviar_mensagem(chat_id, f"Mensagem recebida! Você já mandou {novo_contador} mensagem(ns).")
                except Exception as e:
                    logging.error(f"Erro no banco: {e}")
                    enviar_mensagem(chat_id, "Ocorreu um erro ao salvar seus dados.")

def main():
    init_db()
    offset = 0
    logging.info("Bot leve iniciado e escutando mensagens...")
    
    while True:
        try:
            response = requests.get(f"{URL_API}/getUpdates", params={"offset": offset, "timeout": 30})
            data = response.json()
            
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    processar_mensagens([update])
        except Exception as e:
            logging.error(f"Erro na conexão com o Telegram: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()