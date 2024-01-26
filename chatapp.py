import io
import dotenv
import os
from dotenv import load_dotenv
dotenv_path = os.path.join('', '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()
import django
django.setup()
from sales_agent_manager import SalesAgentManager
import pydub
import requests
import soundfile as sf
import speech_recognition as sr
from flask import Flask, jsonify, request
import utils
import ssl
import openai
from objects_creator import create_user_msg, create_ai_msg
import utils
from apps.home.models import ChatUser
import threading

app = Flask(__name__)
sales_agent_manager = SalesAgentManager()
ACCOUNTS_DIR = "Accounts"
RECORDINGS_DIR = "recordings"
crm = utils.crm
# OpenAi API key
openai.api_key = utils.openai_api_key
appid = 'app_37138_1'
email = 'admin@guruai.space'
password = '614c0b4918ca77ec559ff745ca728079'


# make request to OpenAI
def make_openai_request(message, from_number):
    ai_prefix = 'Guru'
    accounts_dir = os.path.join(ACCOUNTS_DIR, str(from_number))
    if not os.path.exists(accounts_dir):
        os.makedirs(accounts_dir)
    history_file_path = os.path.join(accounts_dir, 'history.txt')
    with open(history_file_path, 'a') as file:
        file.close()
    utils.write_to_history(from_number, from_number, message)
    sales_agent = sales_agent_manager.get_sales_agent(from_number)
    sales_agent.human_step(message)
    sales_agent.determine_conversation_stage()
    user, created = ChatUser.objects.get_or_create(user_name=from_number, user_id=from_number,
                                                   messenger='Insta/whatsapp')
    create_user_msg(user, message)
    ai_answer = sales_agent.step()
    utils.write_to_history_assistant(from_number, ai_answer)
    ai_answer = utils.check_dialogue_end_and_print_summary(from_number, ai_answer, message, crm = crm)
    create_ai_msg(user, ai_answer, ai_prefix=ai_prefix)
    return ai_answer


def answer_to_chat(text, user_id):
    token = get_access_token()

    print(f'trying to send answer to WA, text:{text}, to user with number : {user_id}, with token: {token}')
    url = f'https://api.chatapp.online/v1/licenses/43435/messengers/caWhatsApp/chats/{user_id}/messages/text'
    
    payload = {
        "text": text,
    }
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    response = requests.request('POST', url, headers=headers, json=payload)
    print(response.json())

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
    
def get_refresh_token():
    return os.getenv("CHATAPP_REFRESH")


def get_access_token():
    return os.getenv("CHATAPP_ACCESS")

def process_message(text, user_id):
    answer = make_openai_request(text, user_id)
    answer_to_chat(answer, user_id)


# Sets homepage endpoint and welcome message
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        print('Post detected, callback webhook')
        response_data = {'status': 'success', 'message': 'Request processed successfully'}
        data = request.get_json()
        print(data)
        message_data = data.get('data', [])[0].get('message', {})
        chat_data = data.get('data', [])[0].get('chat', {})
        # Извлекаем текст сообщения
        text = message_data.get('text', 'No text found')
        user_id = chat_data.get('id', 'No id found')
        msg_status = data.get('data', [])[0].get('side', {})
        print(f'status message: \n {msg_status}')
        if msg_status == 'in':
            # Start a new thread to process the message asynchronously
            threading.Thread(target=process_message, args=(text, user_id)).start()
        return jsonify(response_data), 200
    print('MESSAGE DETECTED')
    data = request.get_json()
    message_data = data.get('data', [])[0].get('message', {})
    chat_data = data.get('data', [])[0].get('chat', {})
    # Извлекаем текст сообщения
    text = message_data.get('text', 'No text found')
    user_id = chat_data.get('id', 'No id found')
    msg_status = data.get('data', [])[0].get('side', {})
    print(f'status message: \n {msg_status}')
    if msg_status == 'in':
        # Start a new thread to process the message asynchronously
        threading.Thread(target=process_message, args=(text, user_id)).start()
    return '200'


if __name__ == "__main__":
    certfile = '/etc/letsencrypt/live/platform.guruai.space/fullchain.pem'
    keyfile = '/etc/letsencrypt/live/platform.guruai.space/privkey.pem'
    get_new_tokens()
    # Создание SSL контекста
    ssl_context = (certfile, keyfile)
    app.run(debug=True, use_reloader=True, host='0.0.0.0', ssl_context=ssl_context)
