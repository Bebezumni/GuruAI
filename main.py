import dotenv
import requests
from dotenv import dotenv_values
from django.core.files import File
from django.core.files.base import ContentFile
import logging
config = dotenv_values(".env")
print(config)
dotenv.load_dotenv()
import telebot
import utils
from django.conf import settings
import os
from openai import OpenAI
import openai
from uuid import uuid4
import subprocess
from pathlib import Path
import django
from langchain.chat_models import ChatLiteLLM
django.setup()
from apps.home.models import UserMessage, ChatUser, AiAnswer
import threading
import queue
import salesgpt.agents
from salesgpt.agents import SalesGPT
from sales_agent_manager import SalesAgentManager
from objects_creator import create_ai_msg, create_user_msg




# ''''''
openai.api_key = utils.openai_api_key
GPTbot = telebot.TeleBot(utils.Token)
print(f"The Bot is online (id: {GPTbot.get_me().id})...")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
message_queue = queue.Queue()
sales_agent_manager = SalesAgentManager()
ACCOUNTS_DIR = "Accounts"
RECORDINGS_DIR = "recordings"
crm = utils.crm
# ''''''


def make_openai_request(message, from_number, user_name):
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
    user, created = ChatUser.objects.get_or_create(user_name=user_name, user_id=from_number,
                                                   messenger='Site message')
    create_user_msg(user, message)
    ai_answer = sales_agent.step()
    utils.write_to_history_assistant(from_number, ai_answer)
    ai_answer = utils.check_dialogue_end_and_print_summary(from_number, ai_answer, message, crm=crm)
    create_ai_msg(user, ai_answer, ai_prefix=ai_prefix)
    return ai_answer
def create_msg_from_site(id, text):
    GPTbot.send_message(id, text)

def process_messages():
    while True:
        message = message_queue.get()
        chat_id = message.chat.id
        GPTbot.send_chat_action(chat_id=chat_id, action="typing")
        print('message started to process')
        user_id = message.from_user.id
        user_profile_photos = GPTbot.get_user_profile_photos(user_id)
        print(user_profile_photos)
        user_name = message.from_user.first_name
        file_path = f'Accounts/{user_id}/history.txt'
        token_count = utils.count_tokens(file_path)
        print(f'Количество токенов в файле: {token_count}')
        if token_count > 3000:
            print('Токенов больше 3000. Очищаем файл.')
            utils.clear_file(file_path)
            print('Файл очищен.')
        else:
            print('Токенов меньше или равно 3000. Файл не требует очистки.')
        if user_profile_photos.photos:
            first_photo = user_profile_photos.photos[0][0]
            file_id = first_photo.file_id
            file_path = GPTbot.get_file(file_id).file_path
            photo_url = f'https://api.telegram.org/file/bot{GPTbot.token}/{file_path}'
            user, created = ChatUser.objects.get_or_create(
                user_name=user_name,
                user_id=user_id,
                messenger='Telegram',
                messenger_id=message.chat.id
            )
            # # Download and save the file using the FileField
            # content = requests.get(photo_url).content
            # user.profile_photo.save(f'file_{user.id}.jpg', ContentFile(content))
            #
            # print(f"User's photo downloaded and saved: {user.profile_photo.url}")
        else:
            user, created = ChatUser.objects.get_or_create(user_name=user_name, user_id=user_id, messenger='Telegram', messenger_id=message.chat.id)
            print('user without photo created or retrieved')
        if message.content_type == "text":
            user_promt = message.text.strip()
            print(f'user promt: {user_promt}')
        elif message.content_type == "voice":
            logger.info('Audio message found')
            file_info = GPTbot.get_file(message.voice.file_id)
            file_path = file_info.file_path
            downloaded_file = GPTbot.download_file(file_path)
            uuid = uuid4()
            filename = Path(__file__).parent / f'{RECORDINGS_DIR}/{uuid}.ogg'
            with open(filename, 'wb') as f:
                f.write(downloaded_file)
            wav_filename = Path(__file__).parent / f'{RECORDINGS_DIR}/{uuid}.wav'
            print(f'WAV CREATED AT {wav_filename}')
            subprocess.run(
                ['ffmpeg', '-i', str(filename), '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16k',
                 str(wav_filename)],
                check=True)
            user_promt = utils.speech_to_text(str(wav_filename))
            print(f'WHISPER SUCCESS PROMT:\n{user_promt}')
            os.remove(filename)
            os.remove(wav_filename)
        create_user_msg(user, user_promt)
        utils.write_to_history(user_id, user_name, user_promt)
        sales_agent = sales_agent_manager.get_sales_agent(user_id)
        sales_agent.human_step(user_promt)
        sales_agent.determine_conversation_stage()
        ai_answer = sales_agent.step()
        ai_answer = utils.check_dialogue_end_and_print_summary(user_id, ai_answer, user_promt, crm=crm)
        create_ai_msg(user, ai_answer, 'Guru')
        utils.write_to_history_assistant(user_id, ai_answer)
        ai_answer = utils.check_bali_code(GPTbot, chat_id, ai_answer, user_promt)
        GPTbot.reply_to(message=message, text=ai_answer.replace('<PHOTO_CODE>', ''))
        ai_answer = utils.check_photo_code(GPTbot, chat_id, ai_answer, user_promt)
        message_queue.task_done()
        print('message task done')

@GPTbot.message_handler(commands=["start"])
def start_command_handler(message: callable) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    accounts_dir = os.path.join(ACCOUNTS_DIR, str(user_id))
    if not os.path.exists(accounts_dir):
        os.makedirs(accounts_dir)
    history_file_path = os.path.join(accounts_dir, 'history.txt')
    with open(history_file_path, 'w+') as file:
        file.truncate(0)
    GPTbot.send_chat_action(chat_id=message.chat.id, action="typing")
    user_prompt = 'Привет'
    sales_agent = sales_agent_manager.get_sales_agent(user_id)
    sales_agent.human_step(user_prompt)
    sales_agent.determine_conversation_stage()
    ai_answer = sales_agent.step()
    GPTbot.reply_to(message=message, text=ai_answer)
    user, created = ChatUser.objects.get_or_create(user_name=user_name, user_id=user_id, messenger='Telegram', messenger_id=message.chat.id)
    create_ai_msg(user, ai_answer, 'Guru')
@GPTbot.message_handler(content_types=["text", "voice"])
def handle_text(message):
    message_queue.put(message)
if __name__ == "__main__":
    try:
        threading.Thread(target=process_messages, daemon=True).start()
        GPTbot.delete_webhook()
        GPTbot.infinity_polling(skip_pending=True, none_stop=True)
        print('bot polling started')
    except Exception as e:
        print(f"An error occurred: {e}")