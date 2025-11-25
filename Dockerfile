FROM python:3.10-slim

WORKDIR /app

# copiar somente o necessário
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT 8080

# comando padrão
CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4"]
