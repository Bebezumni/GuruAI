import requests
import json
from dotenv import load_dotenv

load_dotenv()


appid = 'app_37138_1'
email = 'admin@guruai.space'
password = '614c0b4918ca77ec559ff745ca728079'
access_token='f06bf73a7603afc3c25b0d29d5373123b95b53f75185aaaa771404b95ff2f8ac'
refresh_token='857025f60e0f22512bfe85d66ad5e23a18d78684827201de1e4a15559f855655'
tokens = {
    'success': True,
    'data': {
        'cabinetUserId': 37138,
        'accessToken': '$2y$10$juLuaxVANnvVlCi81u.Hp./DDOFJry6bB2Bdj7qi/A9aImvYEuCUG',
        'accessTokenEndTime': 1706001610,
        'refreshToken': '$2y$10$CrQBVyT8TRjcYJMvw0VZje6pKTLEOVw4sWhpZoL6.iPga9C2YZnya',
        'refreshTokenEndTime': 1707124810
    }}
def is_token_expired(expiration_time):
    current_time = int(time.time())
    return current_time >= expiration_time

# Function to save tokens in .env file
def save_tokens_to_env(access_token, access_token_end_time, refresh_token, refresh_token_end_time):
    with open('.env', 'w') as env_file:
        env_file.write(f'ACCESS_TOKEN={access_token}\n')
        env_file.write(f'ACCESS_TOKEN_END_TIME={access_token_end_time}\n')
        env_file.write(f'REFRESH_TOKEN={refresh_token}\n')
        env_file.write(f'REFRESH_TOKEN_END_TIME={refresh_token_end_time}\n')

def get_tokens():
    url = 'https://api.chatapp.online/v1/tokens'
    payload = {
        "email": email,
        "password": password,
        "appId": appid
    }
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request('POST', url, headers=headers, json=payload)
    print(response.json())



def answer_to_chat(text, user_id):
    url = f'https://api.chatapp.online/v1/licenses/43435/messengers/caWhatsApp/chats/{user_id}/messages/text'
    print(access_token)
    payload = {
        "text": text,
    }
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }
    response = requests.request('POST', url, headers=headers, json=payload)
    print(f'Зарос отправлен на {user_id}, ответ :{response.json()}')

# answer_to_chat('Hey', '79160126308')

def refresh_ca_token():
    url = 'https://api.chatapp.online/v1/tokens/refresh'
    headers = {
        'Refresh': refresh_token
    }

    response = requests.request('POST', url, headers=headers)

    print(response.json())
def set_callback():
    url = 'https://api.chatapp.online/v1/licenses/43435/messengers/caWhatsApp/callbackUrl'
    payload = {
        "events": [
            "message",
            "messageStatus"
        ],
        "url": "https://platform.guruai.space:5000"
    }
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }

    response = requests.request('PUT', url, headers=headers, json=payload)
    print(response.json())

def get_license():
    url = 'https://api.chatapp.online/v1/licenses'
    headers = {
        'Authorization': access_token
    }

    response = requests.request('GET', url, headers=headers)
    response.json()
    print(response.json())


def get_templates():
    url = 'https://api.chatapp.online/v1/licenses/43435/messengers/caWhatsApp/templates'
    headers = {
        'Authorization': access_token
    }
    print(access_token)
    response = requests.request('GET', url, headers=headers)
    print(response.json())


def send_template():

    url = 'https://api.chatapp.online/v1/licenses/43435/messengers/caWhatsApp/chats/79998331625/messages/template'
    name = 'Arseniy'
    payload = {
        "template": {
            "id": "680246037632141",
            "params": [
                f"{name}"
            ]

        },
        "file": "https:\/\/download.samplelib.com\/jpeg\/sample-green-400x300.jpg",
        "fileName": "sample-green-400x300.jpg",
        "tracking": "velit",
        "companyId": 14
    }
    print(access_token)
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }

    response = requests.request('POST', url, headers=headers, json=payload)
    print(response.json())


def get_callback():
    url = 'https://api.chatapp.online/v1/callbackUrls'
    headers = {
        'Authorization': access_token
    }

    response = requests.request('GET', url, headers=headers)
    print(response.json())
    return 200

get_tokens()
# answer_to_chat('Привет', '79998331625')
# refresh_ca_token()
# send_template()
# get_callback()