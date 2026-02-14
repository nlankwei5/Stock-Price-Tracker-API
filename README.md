# Stock-Price-Tracker-API

Tracks real-time prices for 15 stocks. Fetches from Finnhub every 60 seconds, calculates SMA, and pushes updates to connected clients over WebSocket.

---

## What it does

- Fetches live prices for 15 stocks every 60 seconds via Finnhub API
- Saves prices to PostgreSQL
- Caches the last 5 prices per stock in Redis to calculate a 5-period SMA
- Detects bullish/bearish SMA crossover alerts
- Broadcasts price updates + alerts to WebSocket clients in real time

---

## Future addtions

- Simple frontend to show how it works
- Making sure API calls are not made when market closes. This should be done automatically.
- Migrate database to PostgreSQL

---

## Stack

- **Django + DRF** — API
- **Celery + Celery Beat** — background task scheduling
- **Redis** — caching and Channels backend
- **Django Channels** — WebSocket support
- **Uvicorn** — ASGI server
- **Finnhub** — stock price data
- **SQLite** — database(development environment)

---

## Setup

```bash
git clone https://github.com/yourusername/stock-price-tracker-api.git
cd stock-price-tracker-api

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file:

```
API_KEY=your_finnhub_api_key
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/stockdb
```

Run migrations:

```bash
python manage.py migrate
```

---
