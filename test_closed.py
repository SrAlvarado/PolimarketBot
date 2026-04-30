import requests
import json

url = "https://gamma-api.polymarket.com/events?active=false&closed=true&limit=1"
response = requests.get(url)
print(json.dumps(response.json()[0]['markets'][0], indent=2))
