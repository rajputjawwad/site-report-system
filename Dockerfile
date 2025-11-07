# Use Debian base for wkhtmltopdf compatibility
FROM python:3.10-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb && \
    apt-get install -y ./wkhtmltox_0.12.6-1.bullseye_amd64.deb || apt-get install -f -y && \
    rm -f wkhtmltox_0.12.6-1.bullseye_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
