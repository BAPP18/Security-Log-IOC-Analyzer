FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin bluelens

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/database /app/uploads /app/exports /app/reports /app/logs \
    && chown -R bluelens:bluelens /app

USER bluelens

ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["sh", "-c", "gunicorn --workers 1 --threads 2 --timeout 180 'app:create_app()' --bind 0.0.0.0:$PORT"]
