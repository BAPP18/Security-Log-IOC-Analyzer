FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY . .

ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY=bluelens-secret-key-2024

EXPOSE 8000

CMD gunicorn --workers 1 --threads 2 --timeout 180 'app:create_app()' --bind 0.0.0.0:$PORT