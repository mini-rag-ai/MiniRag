FROM python:3.10-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev libxslt1-dev libffi-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY src/requirements.txt .
RUN uv pip install -r requirements.txt --system

COPY src/ .

RUN mkdir -p /app/models/db_schemes/minirag/
COPY docker/minirag/alembic.ini /app/models/db_schemes/minirag/alembic.ini

COPY docker/minirag/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--port", "8000", "--workers", "4"]
