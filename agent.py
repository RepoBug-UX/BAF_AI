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
        return {}

CRYPTO_MAPPINGS = get_crypto_metadata()

def parse_crypto_query(query: str) -> str:
    """Extract cryptocurrency symbol from a natural language query."""
    patterns_to_remove = [
        "what is", "what's", "whats",
        "how much is", "tell me",
        "show me", "give me",
        "current price of", "price of",
        "the price of", "the current price of"
    ]
    
    query = query.lower()
    
    # Remove patterns
    for pattern in patterns_to_remove:
        query = query.replace(pattern, "")
    
    query = query.strip()
    
    upper_symbols = re.findall(r'\b[A-Z]{2,5}\b', query.upper())
    for symbol in upper_symbols:
        if symbol in CRYPTO_MAPPINGS.values():
            return symbol
    
    words = [word.strip('?.,!') for word in query.split()]
    
    if not words:
        return None
        
    last_word = words[-1].lower()
    
    if last_word in CRYPTO_MAPPINGS:
        return CRYPTO_MAPPINGS[last_word]
    
    return None

def fetch_crypto_price(symbol: str, convert: str = "USD"):
    """Fetch the latest price of a specified cryptocurrency."""
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        return "Error: API key is required. Please set COINMARKETCAP_API_KEY in your .env file"

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
            return f"Error: Cryptocurrency {symbol} not found"
            
        price = data["data"][symbol]["quote"][convert]["price"]
        name = data["data"][symbol]["name"]
        return f"The current price of {name} ({symbol}) is {price:,.8f} {convert}"
        
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to fetch cryptocurrency price: {e}"

def handle_message(message, context):
    """Handle incoming messages for the agent."""
    query = message.get('content', '').strip()
    
    if not query:
        return "Please ask me about a cryptocurrency price!"
        
    symbol = parse_crypto_query(query)
    if symbol:
        return fetch_crypto_price(symbol)
    else:
        return "Sorry, I couldn't identify which cryptocurrency you're asking about. Please specify the cryptocurrency at the end of your question."