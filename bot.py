import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai
from google.genai import types

# Configuração de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Leitura e limpeza das variáveis de ambiente (remove espaços acidentais)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Validação rápida das chaves
if not TELEGRAM_TOKEN:
    raise ValueError("ERRO: TELEGRAM_TOKEN não está definido nas variáveis de ambiente!")
if not GEMINI_API_KEY:
    raise ValueError("ERRO: GEMINI_API_KEY não está definido nas variáveis de ambiente!")

# Configuração da nova API do Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Você é o ArrieguaIA, um assistente avançado de inteligência artificial focado estritamente em Cibersegurança, 
Pentesting (Ofensivo e Defensivo), Análise de Código Seguro, Engenharia Reversa, Redes e DevSecOps. 
Seu objetivo é ajudar profissionais de segurança, estudantes e entusiastas a entender vulnerabilidades, 
corrigir códigos inseguros e debater técnicas de proteção e mitigação de riscos. 
Responda sempre com precisão técnica, clareza e mantenha um tom profissional.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Fala, {user_name}! 🛡️ Sou o teu assistente especializado em Cibersegurança.\n\n"
        "Podes mandar-me dúvidas sobre segurança da informação, análise de código, pentesting, redes ou vulnerabilidades!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Chamada utilizando o novo client do Gemini 2.5 / Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("Ocorreu um erro ao processar a tua consulta de segurança. Tenta novamente em instantes.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot de Cibersegurança iniciado e a aguardar mensagens...")
    app.run_polling()

if __name__ == '__main__':
    main()
