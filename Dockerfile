FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Just expose a static port for documentation
EXPOSE 10000

# Use shell form so $PORT expands at runtime
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
