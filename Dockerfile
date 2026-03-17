FROM python:3.12.0-alpine

RUN addgroup -S appuser && adduser -S appuser -G appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/wallet_project

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

RUN chmod 777 -R /usr/src/wallet_project

USER appuser