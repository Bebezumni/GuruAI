import io
import os
import dotenv
dotenv.load_dotenv()
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

# OpenAi API key
openai.api_key = utils.openai_api_key
token = '$2y$10$TwWFjsbOidKKqGxF0F35c.SWtnFpkLAWMaqDZcSXo7kM7BTumz2p.'


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
    ai_answer = utils.check_dialogue_end_and_print_summary(from_number, ai_answer, message)
    create_ai_msg(user, ai_answer, ai_prefix=ai_prefix)
    return ai_answer


def answer_to_chat(text, user_id):
    url = f'https://api.chatapp.online/v1/licenses/43053/messengers/instagram/chats/{user_id}/messages/text'
    payload = {
        "text": text,
    }
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    response = requests.request('POST', url, headers=headers, json=payload)
    print(response.json())


def process_message(text, user_id):
    answer = make_openai_request(text, user_id)
    answer_to_chat(answer, user_id)


# Sets homepage endpoint and welcome message
@app.route("/", methods=["GET", "POST"])
def home():
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


# @app.route("/callback", methods=["GET", "POST"])
# def callback():
#     print(request.get_json())
#     return '200'

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host='0.0.0.0')
