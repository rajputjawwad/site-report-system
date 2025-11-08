# Use Debian-based Python image for compatibility
FROM python:3.10-bullseye

WORKDIR /app

# Install system dependencies + LibreOffice
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        wget \
        fontconfig \
        libfreetype6 \
        libjpeg62-turbo \
        libpng16-16 \
        libx11-6 \
        libxcb1 \
        libxext6 \
        libxrender1 \
        xfonts-75dpi \
        xfonts-base && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
