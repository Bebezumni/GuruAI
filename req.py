

import requests

api_version = "v18.0"
whatsapp_business_account_id = "168724609661438"
access_token = "EAANfmCTCQNsBO91RVJovulQK1ZABkHxYoGqCTotNQ0cNGHMAZA0xR4ZB3MeoQ4Nt73UnzSzeAnQpKgAmLZAL16vGeYFEbcTjqcmV93daWmE9ctnF4Ef2ZCN7MPZCHTJbGflNzFD8ydByxGMZAbvdXV4BZC63C7kgsmcOaiDw9Wrknzah5l4Clm3TOLp7UwRkZABFWCkJZB8vG0UyMu4xkKY1NNzqyr3j4oHkAUJSt7yxxhAKQZD"

url = f'https://graph.facebook.com/{api_version}/{whatsapp_business_account_id}/subscribed_apps'
headers = {
    'Authorization': f'Bearer {access_token}',
}

response = requests.post(url, headers=headers)

# Verify the response
if response.status_code == 200:
    print("Subscribed to app successfully!")
else:
    print(f"Failed to subscribe to app. Status Code: {response.status_code}")
    print(response.text)