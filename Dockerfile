FROM python:3.10-slim

WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodu kopyala
COPY bot.py .

# Botu arka planda sürekli çalıştır
CMD ["python", "bot.py"]