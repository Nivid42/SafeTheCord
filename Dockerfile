# --- Base Image ---
FROM python:3.12-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY config.ini .
COPY .env .
COPY cogs/ ./cogs/
COPY data/ ./data/

# Startbefehl
CMD ["python", "bot.py"]

