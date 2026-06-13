import os
import logging
import requests
from flask import Flask, request
from groq import Groq

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(url, data=data, timeout=30)
        if resp.status_code != 200:
            logging.error(f"Telegram API Hatası: {resp.text}")
    except Exception as e:
        logging.error(f"Mesaj gönderme hatası: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_message = update['message'].get('text', '')
        
        if user_message == '/start':
            send_message(chat_id, "Merhaba! Ben senin 7/24 çalışan bulut asistanınım. Bana her şeyi sorabilirsin.")
        else:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_message}],
                    model="llama3-8b-8192",
                    temperature=0.7
                )
                ai_response = chat_completion.choices[0].message.content
                send_message(chat_id, ai_response)
            except Exception as e:
                logging.error(f"AI Hatası: {e}")
                send_message(chat_id, "Şu an AI beynimle iletişim kuramıyorum. Lütfen biraz sonra tekrar dene.")
    
    return '', 200

@app.route('/')
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.environ.get("PORT", 10000))
    
    # Render'da webhook URL'sini otomatik al
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        webhook_url = f"{render_url}/webhook"
        try:
            resp = requests.post(
                f"{TELEGRAM_API_URL}/setWebhook", 
                data={"url": webhook_url}, 
                timeout=30
            )
            if resp.status_code == 200:
                print(f"✅ Webhook başarıyla ayarlandı: {webhook_url}")
            else:
                print(f"❌ Webhook ayarlama hatası: {resp.text}")
        except Exception as e:
            logging.error(f"Webhook ayarlama hatası: {e}")
    
    app.run(host='0.0.0.0', port=port)
