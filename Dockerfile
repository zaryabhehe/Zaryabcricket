FROM python:3.8.5-slim-buster

ENV PIP_NO_CACHE_DIR 1

ENV BOT_TOKEN=7392456702:AAEkFumYEFLORrOiCw9sgpndE74RyQcMEu8
ENV CHAT_ID=-1002465116955

# Install necessary dependencies including wkhtmltoimage
RUN apt-get update && apt-get install -y \
    curl \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    fontconfig && \
    # Send startup message to Telegram
    curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": \"${CHAT_ID}\", \"text\": \"Bot is starting...\"}" && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
RUN pip3 install --upgrade pip setuptools

# Copy application code
COPY . /app/

# Set working directory
WORKDIR /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Run the bot
CMD ["python3", "-m", "TEAMZYRO"]
