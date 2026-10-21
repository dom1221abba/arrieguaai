import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Carrega as variáveis de ambiente locais do .env se existir
load_dotenv()

# Configuração de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("ERRO: TELEGRAM_TOKEN ou GEMINI_API_KEY não estão definidos!")

# Inicializa o cliente oficial da biblioteca google-genai
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
        "🟢 **[SISTEMA ONLINE]** ArrieguaIA pronto e protegido contra picos de tráfego!\n\n"
        "Podes mandar-me dúvidas sobre segurança da informação, análise de código, pentesting, redes ou vulnerabilidades!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nPergunta do utilizador: {user_message}"
        
        response = None
        # Tenta o modelo principal mais recente
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=full_prompt
            )
        except Exception as primary_error:
            logging.warning(f"Modelo principal sobrecarregado, a tentar fallback... Erro: {primary_error}")
            # Fallback automático para o gemini-1.5-flash caso o principal dê 503
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=full_prompt
            )
        
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Erro crítico ao consultar a IA: {e}")
        await update.message.reply_text("⚠️ Os servidores da IA estão temporariamente com pico de tráfego. Tenta enviar a mensagem novamente em instantes.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot de Cibersegurança iniciado e a aguardar mensagens...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
