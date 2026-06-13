import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from groq import Groq

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Ben senin 7/24 çalışan bulut asistanınım. Bana her şeyi sorabilirsin.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    await context.bot.send_chat_action(chat_id=user_id, action="typing")

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama3-8b-8192",
            temperature=0.7
        )
        ai_response = chat_completion.choices[0].message.content
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logging.error(f"Hata: {e}")
        await update.message.reply_text("Şu an AI beynimle iletişim kuramıyorum. Lütfen biraz sonra tekrar dene.")

def main():
    # Ağ bağlantısı için daha esnek ve dayanıklı ayarlar
    request = HTTPXRequest(connection_pool_size=8, connect_timeout=30.0, read_timeout=30.0)
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot başlatıldı, 7/24 dinlemede...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()