# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies for pdfkit + wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates fontconfig libxrender1 libxext6 libjpeg62-turbo libpng16-16 && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb && \
    apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb && \
    rm -rf /var/lib/apt/lists/* wkhtmltox_0.12.6-1.buster_amd64.deb

# Copy all project files
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
