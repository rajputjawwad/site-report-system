# Use full Debian image for LibreOffice support
FROM python:3.10-bullseye

WORKDIR /app

# Install LibreOffice + dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-common \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
        libreoffice-core \
        fonts-dejavu-core \
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
    libreoffice --version && \
    rm -rf /var/lib/apt/lists/*

# Copy your project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Start Flask with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
