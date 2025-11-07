# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for pdfkit / wkhtmltopdf)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    libjpeg-dev libxrender1 libfontconfig1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Command for Render
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
