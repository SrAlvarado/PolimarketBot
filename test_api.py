import requests
import json

url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=2"
response = requests.get(url)
print(json.dumps(response.json(), indent=2))
