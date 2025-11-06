FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    fonts-dejavu-core \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "--workers", "1"]
