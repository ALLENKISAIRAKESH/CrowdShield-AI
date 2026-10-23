# CrowdShield AI — Production Docker Container
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

ENV PORT=8501
EXPOSE 8501

# Launch Streamlit app (respects Render's dynamic $PORT or defaults to 8501)
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
