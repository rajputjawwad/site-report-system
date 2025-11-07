# Use full Debian base for wkhtmltopdf compatibility
FROM python:3.10-bullseye

WORKDIR /app

# Install system dependencies and wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    fontconfig \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && apt install -y ./wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && rm -f wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
