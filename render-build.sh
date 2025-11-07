#!/usr/bin/env bash
# ===============================
# Render build script
# Installs wkhtmltopdf before Flask app setup
# ===============================

apt-get update
apt-get install -y wkhtmltopdf

echo "✅ wkhtmltopdf installed successfully"
