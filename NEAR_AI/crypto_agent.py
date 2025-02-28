import requests
import os
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
        print(f"Failed to fetch crypto data: {e}")
        return {}

CRYPTO_MAPPINGS = get_crypto_metadata()

def parse_crypto_query(query: str) -> str:
    """Extract cryptocurrency symbol from a natural language query."""
    filters = [
        "what is", "what's", "whats",
        "how much is", "tell me",
        "show me", "give me",
        "current price of", "price of",
        "the price of", "the current price of"
    ]
    
    query = query.lower()
    for f in filters:
        query = query.replace(f, "")
    
    words = [word.strip('?.,!') for word in query.split()]
    if not words:
        return None
        
    last_word = words[-1].lower()
    
    if last_word in CRYPTO_MAPPINGS:
        return CRYPTO_MAPPINGS[last_word]
    
    if last_word.upper() in CRYPTO_MAPPINGS.values():
        return last_word.upper()
    
    return None

def get_crypto_price(symbol: str, convert: str = "USD"):
    """Fetch the latest price of a specified cryptocurrency."""
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        print("Missing API key - add COINMARKETCAP_API_KEY to .env file")
        return None

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key
    }
    params = {
        "symbol": symbol.upper(),
        "convert": convert.upper()
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if symbol not in data.get("data", {}):
            print(f"Couldn't find {symbol}")
            return None
            
        price = data["data"][symbol]["quote"][convert]["price"]
        name = data["data"][symbol]["name"]
        print(f"{name} ({symbol}) is worth {price:,.8f} {convert}")
        return price
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def get_crypto_conversion(base_symbol: str, target_symbol: str):
    """Fetch the conversion rate between two cryptocurrencies.
    
    Args:
        base_symbol: The base cryptocurrency symbol (e.g., BTC)
        target_symbol: The target cryptocurrency symbol (e.g., ETH)
    
    Returns:
        float: The conversion rate, or None if there's an error
    """
    return get_crypto_price(base_symbol, target_symbol)

def handle_crypto_query(query: str):
    """Handle a natural language query about cryptocurrency prices."""
    symbol = parse_crypto_query(query)
    if symbol:
        get_crypto_price(symbol)
    else:
        print("No such crypto exists")

if __name__ == "__main__":
    while True:
        try:
            query = input("> ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit', 'q']:
                break
            handle_crypto_query(query)
        except (KeyboardInterrupt, EOFError):
            break 