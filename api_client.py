# api_client.py

import requests
import os # <--- ADD THIS LINE
from dotenv import load_dotenv # <--- ADD THIS LINE

load_dotenv() # <--- ADD THIS LINE: This will load the .env file

class APIClient:
    def __init__(self):
        # Use os.getenv() to get the key from environment variables
        # The load_dotenv() call above makes these available
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY") # <--- CHANGE THIS LINE
        self.alpha_vantage_base_url = "https://www.alphavantage.co/query"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"

    def get_stock_price(self, symbol):
        """Fetches current stock price using Alpha Vantage."""
        # The check for placeholder key might not be strictly needed if .env is properly loaded
        # but it's good for initial setup validation.
        if not self.alpha_vantage_api_key: # Removed the == "YOUR_ALPHA_VANTAGE_API_KEY" part here.
            print("Alpha Vantage API key not set in .env file. Please check your .env.")
            return None

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_api_key
        }
        try:
            response = requests.get(self.alpha_vantage_base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data and len(data["Global Quote"]) > 0:
                price = float(data["Global Quote"]["05. price"])
                change = float(data["Global Quote"]["09. change"])
                change_percent = data["Global Quote"]["10. change percent"]
                return {"price": price, "change": change, "change_percent": change_percent}
            elif "Error Message" in data:
                print(f"Error fetching {symbol}: {data['Error Message']}")
            else:
                print(f"Unexpected API response for {symbol}: {data}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching {symbol}: {e}")
            return None
        except ValueError as e:
            print(f"Data parsing error for {symbol}: {e}")
            return None

    def get_crypto_price(self, coin_id):
        """Fetches current cryptocurrency price using CoinGecko."""
        params = {
            "ids": coin_id,
            "vs_currencies": "usd"
        }
        try:
            response = requests.get(f"{self.coingecko_base_url}/simple/price", params=params)
            response.raise_for_status()
            data = response.json()
            if coin_id in data and 'usd' in data[coin_id]:
                return {"price": data[coin_id]['usd']}
            elif len(data) == 0:
                print(f"Could not find crypto '{coin_id}'. Please check the CoinGecko ID.")
            else:
                print(f"Unexpected API response for crypto {coin_id}: {data}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching crypto {coin_id}: {e}")
            return None
        except ValueError as e:
            print(f"Data parsing error for crypto {coin_id}: {e}")
            return None

    def get_historical_stock_data(self, symbol, interval="daily", outputsize="compact"):
        """Fetches historical stock data (e.g., daily prices)."""
        if not self.alpha_vantage_api_key: # Removed the == "YOUR_ALPHA_VANTAGE_API_KEY" part here.
            print("Alpha Vantage API key not set in .env file. Please check your .env.")
            return None

        params = {
            "function": "TIME_SERIES_DAILY" if interval == "daily" else "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "apikey": self.alpha_vantage_api_key,
            "outputsize": outputsize
        }
        if interval == "intraday":
            params["interval"] = "5min"

        try:
            response = requests.get(self.alpha_vantage_base_url, params=params)
            response.raise_for_status()
            data = response.json()

            key = "Time Series (Daily)" if interval == "daily" else f"Time Series ({params['interval']})"
            if key in data:
                return data[key]
            elif "Error Message" in data:
                print(f"Error fetching historical data for {symbol}: {data['Error Message']}")
            else:
                print(f"Unexpected API response for historical data {symbol}: {data}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching historical data for {symbol}: {e}")
            return None
        except ValueError as e:
            print(f"Data parsing error for historical data {symbol}: {e}")
            return None

# The print statement is good for debugging, but not essential for functionality.
# print("APIClient class defined.")