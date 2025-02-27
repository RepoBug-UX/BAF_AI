import logging
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

def get_crypto_metadata():
    """Fetch cryptocurrency metadata from CoinMarketCap API."""
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        return {}

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        mappings = {}
        for crypto in data['data']:
            name = crypto['name'].lower()
            symbol = crypto['symbol'].upper()
            mappings[name] = symbol
            mappings[symbol.lower()] = symbol
        return mappings
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch cryptocurrency metadata: {e}")
        return {}

CRYPTO_MAPPINGS = get_crypto_metadata()

def parse_crypto_query(query: str) -> str:
    """Extract cryptocurrency symbol from a natural language query."""
    query = query.lower()
    words = query.split()
 
    for word in words:
        if word in CRYPTO_MAPPINGS:
            return CRYPTO_MAPPINGS[word]
 
    for name, symbol in CRYPTO_MAPPINGS.items():
        if name in query:
            return symbol

    matches = re.findall(r'\b[A-Za-z]{2,5}\b', query)
    for match in matches:
        if match.lower() in CRYPTO_MAPPINGS:
            return CRYPTO_MAPPINGS[match.lower()]
    
    return None

def fetch_crypto_price(symbol: str, convert: str = "USD"):
    """Fetch the latest price of a specified cryptocurrency."""
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        print("Error: API key is required. Please set COINMARKETCAP_API_KEY in your .env file")
        return None

    symbol = symbol.upper()
    convert = convert.upper()

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key
    }
    params = {
        "symbol": symbol,
        "convert": convert
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if symbol not in data.get("data", {}):
            print(f"Error: Cryptocurrency {symbol} not found")
            return None
            
        price = data["data"][symbol]["quote"][convert]["price"]
        name = data["data"][symbol]["name"]
        print(f"The current price of {name} ({symbol}) is {price:,.8f} {convert}")
        return price
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch cryptocurrency price: {e}")
        return None

def fetch_crypto_conversion(base_symbol: str, target_symbol: str):
    """Fetch the conversion rate between two cryptocurrencies.
    
    Args:
        base_symbol: The base cryptocurrency symbol (e.g., BTC)
        target_symbol: The target cryptocurrency symbol (e.g., ETH)
    
    Returns:
        float: The conversion rate, or None if there's an error
    """
    return fetch_crypto_price(base_symbol, target_symbol)

def handle_crypto_query(query: str):
    """Handle a natural language query about cryptocurrency prices."""
    symbol = parse_crypto_query(query)
    if symbol:
        fetch_crypto_price(symbol)
    else:
        print("Sorry, I couldn't identify which cryptocurrency you're asking about.")

if __name__ == "__main__":
    while True:
        query = input("> ").strip()
        if query.lower() in ['exit', 'quit', 'q']:
            break
        handle_crypto_query(query) 