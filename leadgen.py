import dotenv
import jwt
import requests
import time
import logging
from requests.exceptions import JSONDecodeError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

dotenv_path = os.path.join('', '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()


subdomain = os.getenv("AMOCRM_SUBDOMAIN")
client_id = os.getenv("AMOCRM_CLIENT_ID")
client_secret = os.getenv("AMOCRM_CLIENT_SECRET")
redirect_uri = os.getenv("AMOCRM_REDIRECT_URL")
secret_code = "def50200bbb4b474f9566d4fb3a045677918cf906acfb0341bdff56eee9689610923bb9b9e771a1551621ab799fc99e34f34018fbfdd748383561ad6db4dfd28296e5920c48756aa02ed509924ed10b0f0242dbac22ac77e3330e5310288dbe64963bcf4a11df0fb850dc2e147e642a1b01fd26fd413de01dbd49fa7a00399915fe649b5d7efedf7eb40acbce6a87789479511671f0067a6996d1361bc4d92632c0264e31eca87a2143e61465ef02be8fdef372245de304aa7089cc9d3ca0c66c68a169a85b51ad282e71ed93c6a95b9c503ed0e7f25ec17a874e7a327f9b7d4edd72c8ddccb37da5c771394722f8a366cc5c8b00c53ec5ce573e8f2d483677be932782ad34c5921fe8830ab41f63579f90fdd7f8a293568e0ba365935dd40ff45ddfdf085c62c32ccd4eaf6cab20e28412c9b76cdf82ba21cb0551f4269311ff15d9f313131928477bb83fb59bc328ca8d19760813f56eba3da8cd77aa5740d8fce2b1463f90c26040f1101b14de9f57210dfd51672200e60855721f57f18a36e75565b75b7e0a2beda399298099c3d31e49e8223dc2923349fca8b986eeba0970177b2f9b1f20e0c24b362b7f3de0002b1f6148ecbfc4275f9523c951d21630dc6eeb7f98ec718cfafa14b38176420097227e6b075f60808d1fff6ecd7462ca634e633c3b978bc84879d6f74"

def _is_expire(token: str):
    token_data = jwt.decode(token, options={"verify_signature": False})
    exp = datetime.utcfromtimestamp(token_data["exp"])
    now = datetime.utcnow()
    return now >= exp


import jwt
from datetime import datetime, timedelta


def is_minute_passed(token: str, issuance_window_minutes=1):
    try:
        token_data = jwt.decode(token, options={"verify_signature": False})

        # Use the current time instead of 'iat'
        now = datetime.utcnow()

        # Calculate the time difference in minutes
        iat_timestamp = token_data["iat"]
        iat_datetime = datetime.utcfromtimestamp(iat_timestamp)
        time_difference = (now - iat_datetime).total_seconds() / 60

        print("Issuance Time:", iat_datetime)
        print("Current Time:", now)
        print("Time Difference (minutes):", time_difference)

        return time_difference >= issuance_window_minutes
    except jwt.ExpiredSignatureError:
        print("Token is already expired.")
        return True
    except jwt.DecodeError:
        print("Error decoding token.")
        return False

def _save_tokens(access_token: str, refresh_token: str):
    # Записываем в ключи .env
    os.environ["AMOCRM_ACCESS_TOKEN"] = access_token
    os.environ["AMOCRM_REFRESH_TOKEN"] = refresh_token
    dotenv.set_key(dotenv_path, "AMOCRM_ACCESS_TOKEN", os.environ["AMOCRM_ACCESS_TOKEN"])
    dotenv.set_key(dotenv_path, "AMOCRM_REFRESH_TOKEN", os.environ["AMOCRM_REFRESH_TOKEN"])


def _get_refresh_token():
    return os.getenv("AMOCRM_REFRESH_TOKEN")


def _get_access_token():
    return os.getenv("AMOCRM_ACCESS_TOKEN")

def _get_new_tokens():
    data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": _get_refresh_token(),
            "redirect_uri": redirect_uri
    }
    response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(subdomain), json=data).json()
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]
    _save_tokens(access_token, refresh_token)




class AmoCRMWrapper:
    def init_oauth2(self):
        if len(_get_access_token()) > 10:
            print('token exists')
            if is_minute_passed(_get_access_token(), issuance_window_minutes=10080):
                _get_new_tokens()
                data = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": 'refresh_token',
                    "refresh_token": _get_refresh_token(),
                    "redirect_uri": redirect_uri
                }
                response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(subdomain), json=data).json()
                print(response)
                access_token = response["access_token"]
                refresh_token = response["refresh_token"]
                print(access_token)
                print(refresh_token)
                _save_tokens(access_token, refresh_token)
        else:
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": secret_code,
                "redirect_uri": redirect_uri
            }
            response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(subdomain), json=data).json()
            print(response)
            access_token = response["access_token"]
            refresh_token = response["refresh_token"]
            print(access_token)
            print(refresh_token)
            _save_tokens(access_token, refresh_token)


def debug_token_info(token):
    try:
        token_data = jwt.decode(token, options={"verify_signature": False})
        print("Decoded Token Data:", token_data)
        return token_data
    except jwt.ExpiredSignatureError:
        print("Token is already expired.")
        return None
    except jwt.JWTDecodeError:
        print("Error decoding token.")
        return None

# Call this function when you get the access token
token_data = debug_token_info(_get_access_token())
amocrm_wrapper_1 = AmoCRMWrapper()
amocrm_wrapper_1.init_oauth2()


if __name__ == '__main_':
    while True:
        time.sleep(43200)
        access_token = os.getenv("AMOCRM_ACCESS_TOKEN")
        if is_minute_passed(access_token, issuance_window_minutes=10080):
            _get_new_tokens()
            print('Token updated')
        else:
            print('Token is still valid')
