from celery import shared_task
import requests 
from .models import *
import finnhub
from dotenv import load_dotenv
import os
from django.core.cache import cache 
from django.core.cache.backends.redis import RedisCache


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
        

    