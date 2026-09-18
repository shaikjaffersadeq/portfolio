FROM python:3.10-slim

# Prevent Python from writing .pyc and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system libraries for OpenCV, audio DSP, and FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir imageio-ffmpeg streamlit fastapi uvicorn python-multipart

# Copy project source code
COPY . .

# Expose Streamlit (8501) and FastAPI (8000)
EXPOSE 10000

# Default entry starts Streamlit dashboard
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=10000", "--server.address=0.0.0.0"]
