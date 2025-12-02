FROM python:3.10-slim

# Ensure Python output is not buffered (better logging)
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# ENTRYPOINT simply runs the batch job
ENTRYPOINT ["python", "src/main.py"]
