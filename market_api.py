import requests
import json

BASE_URL = "https://gamma-api.polymarket.com"

def get_active_markets(limit=5):
    """
    Fetches active markets. Sorts them internally or just grabs popular ones.
    Using events endpoint with active=true
    """
    url = f"{BASE_URL}/events?active=true&closed=false&limit=20"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        markets = []
        for event in data:
            if 'markets' in event:
                for m in event['markets']:
                    if m.get('active') and not m.get('closed'):
                        # Solo mercados de tipo binario con liquidez
                        outcomes = json.loads(m.get('outcomes', '[]'))
                        if len(outcomes) == 2 and m.get('bestBid') and m.get('bestAsk'):
                            markets.append({
                                'market_id': m['id'],
                                'title': m.get('question', 'Unknown'),
                                'outcomes': outcomes,
                                'bestBid': m['bestBid'],
                                'bestAsk': m['bestAsk'],
                                'volume': m.get('volumeNum', 0)
                            })
                            
        # Sort by volume to get the most popular
        markets.sort(key=lambda x: x['volume'], reverse=True)
        return markets[:limit]
        
    except Exception as e:
        print(f"Error fetching active markets: {e}")
        return []

def check_market_status(market_id):
    """
    Checks if a market is closed and returns the winning outcome.
    """
    url = f"{BASE_URL}/markets/{market_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        m = response.json()
        
        if m.get('closed'):
            outcomes = json.loads(m.get('outcomes', '[]'))
            outcome_prices = json.loads(m.get('outcomePrices', '[]'))
            
            if len(outcomes) == len(outcome_prices) and len(outcomes) > 0:
                # Find the index with price > 0.5
                for i, price_str in enumerate(outcome_prices):
                    try:
                        if float(price_str) > 0.5:
                            return True, outcomes[i]
                    except:
                        continue
            # Fallback
            return True, "Unknown"
        return False, None
    except Exception as e:
        print(f"Error checking market {market_id}: {e}")
        return False, None

if __name__ == "__main__":
    markets = get_active_markets(3)
    print("Active Markets:")
    print(json.dumps(markets, indent=2))
