# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (LibreOffice + fonts)
RUN apt-get update && apt-get install -y libreoffice fonts-dejavu-core && apt-get clean

# Copy requirement list first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose the port Render will map
EXPOSE 10000

# Start the app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
