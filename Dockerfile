FROM python:3.11-slim

# Install LibreOffice + fonts
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice-core libreoffice-calc libreoffice-writer fonts-dejavu-core && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

ENV PORT=10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "2"]
