# Use official Python runtime as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies for PyQt5, OpenCV, and GUI handling
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    x11-apps \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of project files
COPY . .

# Expose port (if your app uses a web interface)
EXPOSE 5000

# Run app inside a virtual display so PyQt5 and pyautogui won't crash
CMD ["xvfb-run", "-a", "python", "main.py"]
