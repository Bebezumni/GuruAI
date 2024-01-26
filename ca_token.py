import dotenv
import os
import time
from dotenv import load_dotenv
dotenv_path = os.path.join('', '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()
import requests
appid = 'app_37138_1'
email = 'admin@guruai.space'
password = '614c0b4918ca77ec559ff745ca728079'

def get_new_tokens():
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
    a_token = response.json()['data']['accessToken']
    r_token = response.json()['data']['refreshToken']
    save_tokens(a_token, r_token)
    print(a_token)
    return a_token


def save_tokens(access_token: str, refresh_token: str):
    # Записываем в ключи .env
    os.environ["CHATAPP_ACCESS"] = access_token
    os.environ["CHATAPP_REFRESH"] = refresh_token
    dotenv.set_key(dotenv_path, "CHATAPP_ACCESS", os.environ["CHATAPP_ACCESS"])
    dotenv.set_key(dotenv_path, "CHATAPP_REFRESH", os.environ["CHATAPP_REFRESH"])



if __name__ == "__main__":
    while True:
        time.sleep(1080)
        get_new_tokens()
