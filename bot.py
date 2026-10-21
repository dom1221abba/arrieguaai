import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# Configuração de Logs para monitorização
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Leitura das variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configuração da API do Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Instrução do Sistema (Persona estilo DeepHat / Especialista em Segurança)
SYSTEM_PROMPT = """
Você é o ArrieguaIA, um assistente avançado de inteligência artificial focado estritamente em Cibersegurança, 
Pentesting (Ofensivo e Defensivo), Análise de Código Seguro, Engenharia Reversa, Redes e DevSecOps. 
Seu objetivo é ajudar profissionais de segurança, estudantes e entusiastas a entender vulnerabilidades, 
corrigir códigos inseguros e debater técnicas de proteção e mitigação de riscos. 
Responda sempre com precisão técnica, clareza e mantenha um tom profissional.
"""

# Inicialização do modelo
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start para boas-vindas."""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Fala, {user_name}! 🛡️ Sou o teu assistente especializado em Cibersegurança.\n\n"
        "Podes mandar-me dúvidas sobre segurança da informação, análise de código, pentesting, redes ou vulnerabilidades!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa todas as mensagens de texto usando o Gemini."""
    user_message = update.message.text
    
    try:
        # Envia feedback visual no Telegram ("a digitar...")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Gera a resposta via Gemini API
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("Ocorreu um erro ao processar a tua consulta de segurança. Tenta novamente em instantes.")

def main():
    """Inicia o servidor do bot no Telegram."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registos dos handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot de Cibersegurança iniciado e a aguardar mensagens...")
    app.run_polling()

if __name__ == '__main__':
    main()
