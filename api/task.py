from email import message
from celery import shared_task
import requests 
from .models import *
import finnhub
from dotenv import load_dotenv
import os
from django.core.cache import cache
from django_redis import get_redis_connection

load_dotenv()

API_KEY = os.getenv("API_KEY")

tickers = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "TSLA",
    "META",
    "NVDA",
    "NFLX",
    "BRK.B",
    "JNJ",
    "V",
    "PG",
    "DIS",
    "JPM",
    "KO"
]

finnhub_client = finnhub.Client(api_key=API_KEY)

@shared_task( autoretry_for=(requests.RequestException,), max_retries=5,  retry_backoff=True)
def ingest_stock_prices():
    """
    A task to ingest stock prices.
    """

    stocks_to_be_created = []
    
    for ticker in tickers:
        try:
            response = finnhub_client.quote(ticker)
            
            if response.get('c') and response['c'] > 0:
                stocks_to_be_created.append(
                    Stock(
                        stock=ticker,
                        price=response['c'],
                    )
                )
            else:
                print(f"Invalid price data for {ticker}")
                
        except Exception as e:
            print(f"Error fetching {ticker}: {str(e)}")
            continue
    
    if stocks_to_be_created:
        Stock.objects.bulk_create(stocks_to_be_created)
        print(f"Successfully created {len(stocks_to_be_created)} stock price records")
    else:
        print("No stock prices to create")

    stock_results = []
    print("Updating Redis cache...")

    for stock_obj in stocks_to_be_created:
        result = save_stock_prices(
            ticker=stock_obj.stock,
            price=float(stock_obj.price)
        )
        if result:
            stock_results.append(result)
    
    print(f"✓ Cache update complete. Processed {len(stock_results)} stocks")

    from django.utils import timezone

    message = {
        "type": "stock_update",
        "timestamp": timezone.now().isoformat(),
        "stocks": stock_results
    }

    publish_to_channels(message)
        

def save_stock_prices(ticker, price):
    """Update Redis cache and detect alerts for a single stock."""

    prices_key = f"stock:{ticker}:prices"  
    sma_key = f"stock:{ticker}:sma"        

    redis_client = get_redis_connection("default")

    pipe = redis_client.pipeline()
    pipe.lrange(prices_key, 0, -1)  
    pipe.get(sma_key)                
    results = pipe.execute()

    cached_prices_json = results[0] 
    previous_sma_bytes = results[1]

    if cached_prices_json:
        cached_prices = [
            float(p.decode("utf-8")) if isinstance(p, bytes) else float(p)
            for p in cached_prices_json
        ]
    else:
        cached_prices = []
    
    if previous_sma_bytes:
        previous_sma = float(previous_sma_bytes.decode('utf-8'))
    else:
        previous_sma = None

    previous_price = cached_prices[-1] if cached_prices else None
    prices_for_sma = cached_prices + [price]
    prices_for_sma = prices_for_sma[-5:]
    
    if len(prices_for_sma) == 5:
        current_sma = sum(prices_for_sma) / 5
    else:
        current_sma = None
    
    pipe = redis_client.pipeline()
    pipe.rpush(prices_key, price)
    pipe.ltrim(prices_key, -5, -1)
    pipe.set(sma_key, current_sma)
    pipe.execute()

    should_alert = False
    alert_type = None
    
    if previous_price is not None and previous_sma is not None:
        if previous_price < previous_sma and price > current_sma:
            should_alert = True
            alert_type = 'bullish'
        elif previous_price > previous_sma and price < current_sma:
            should_alert = True
            alert_type = 'bearish'
    
    if should_alert:
        print(f"🚨 ALERT: {ticker} - {alert_type.upper()} crossover!")

    print(f"✓ {ticker}: Price=${price:.2f}, SMA={current_sma}, Cached={len(prices_for_sma)} prices")

    return {
        "ticker": ticker,
        "price": price,
        "sma": round(current_sma, 2) if current_sma else None,
        "alert": alert_type,
    }


def publish_to_channels(message):
    """

    Publish message to all connected WebSocket clients.

    """
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
            "stock_updates",
            message
        )

    print(f"📡 Published {len(message['stocks'])} stocks to WebSocket clients")