FROM python:3.8-slim-buster
WORKDIR /app

# --- Install Google Chrome and required OS packages ---
RUN apt-get update && apt-get install -y wget gnupg2 unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean
# ------------------------------------------------------

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Using the recommended exec form for CMD
CMD ["python3", "main.py"]
