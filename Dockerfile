FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4"]
