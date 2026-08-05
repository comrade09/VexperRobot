FROM python:3.10-slim
WORKDIR /app

# --- Install Chromium and its exact matching driver ---
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*
# ----------------------------------------------------

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
