# Backend Dockerfile dynamically bundling NLP models caching securely
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies resolving DB extensions natively
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy explicitly requirements resolving PIP installs caching isolated natively
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-fetch SpaCy English bounds limiting runtime delays efficiently
RUN python -m spacy download en_core_web_sm

# Bundle application codes structurally
COPY . .

# Initialize explicit folder mappings bypassing permission traps securely
RUN mkdir -p /app/uploads

# Configure deployment binding shell scripts securely checking migrations dynamically
RUN chmod +x ./entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
