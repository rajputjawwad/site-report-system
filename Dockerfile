FROM python:3.11-slim

WORKDIR /app

# Install dependencies for wkhtmltopdf
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    libxext6 \
    wget \
    && apt-get clean

# Download and install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get install -f -y \
    && rm wkhtmltox_0.12.6-1.buster_amd64.deb

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE $PORT

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "--workers", "1"]
