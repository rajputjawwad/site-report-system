# Use Debian base for LibreOffice support
FROM python:3.10-bullseye

WORKDIR /app

# Install LibreOffice + dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        fonts-dejavu \
        fonts-liberation \
        libxrender1 libxext6 libfontconfig1 && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Start Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
