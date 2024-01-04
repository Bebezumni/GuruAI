import dotenv
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
from sales_agent_manager import SalesAgentManager
from objects_creator import create_ai_msg, create_user_msg
openai.api_key = utils.openai_api_key
from salesgpt.agents import SalesGPT
GPTbot = telebot.TeleBot(utils.Token)
print(f"The Bot is online (id: {GPTbot.get_me().id})...")
import salesgpt.agents
ACCOUNTS_DIR = "Accounts"
RECORDINGS_DIR = "recordings"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
message_queue = queue.Queue()
llm = ChatLiteLLM(temperature=0.4, model_name="gpt-3.5-turbo")
sales_agent_manager = SalesAgentManager()
import requests


def create_msg_from_site(id, text):
    GPTbot.send_message(id, text)

image1='im1.jpg'
image2='im2.jpg'
image3='im3.jpg'

def count_tokens(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            tokens = content.split()
        return len(tokens)
    except FileNotFoundError:
        print(f'File "{file_path}" not found. Skipping.')
        return 0

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('')  # Очищаем файл, записывая пустую строку



def check_photo_code(GPTbot, chat_id, assistant_response, promt):
    if '<PHOTO_CODE>' in assistant_response:
        print('Photo code detected')
        assistant_response = assistant_response.replace('<PHOTO_CODE>', '')
        GPTbot.send_photo(chat_id, open(image1, 'rb'))
        GPTbot.send_photo(chat_id, open(image2, 'rb'))
        GPTbot.send_photo(chat_id, open(image3, 'rb'))
    return assistant_response


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

        # Подсчет токенов
        token_count = count_tokens(file_path)
        print(f'Количество токенов в файле: {token_count}')

        # Проверка и очистка файла
        if token_count > 3000:
            print('Токенов больше 3000. Очищаем файл.')
            clear_file(file_path)
            print('Файл очищен.')
        else:
            print('Токенов меньше или равно 3000. Файл не требует очистки.')
        if user_profile_photos.photos:
            first_photo = user_profile_photos.photos[0][0]
            file_id = first_photo.file_id
            file_path = GPTbot.get_file(file_id).file_path
            photo_url = f'https://api.telegram.org/file/bot{GPTbot.token}/{file_path}'
            #
            user, created = ChatUser.objects.get_or_create(
                user_name=user_name,
                user_id=user_id,
                messenger='Telegram',
                messenger_id=message.chat.id
            )
            #
            # # Download and save the file using the FileField
            # content = requests.get(photo_url).content
            # user.profile_photo.save(f'file_{user.id}.jpg', ContentFile(content))
            #
            # print(f"User's photo downloaded and saved: {user.profile_photo.url}")
        else:
            user, created = ChatUser.objects.get_or_create(user_name=user_name, user_id=user_id, messenger='Telegram',
                                                           messenger_id=message.chat.id)
            print('user without photo created or retrieved')

        if message.content_type == "text":
            user_promt = message.text.strip()
            create_user_msg(user, user_promt)
            utils.write_to_history(user_id, user_name, user_promt)
            print(f'user promt: {user_promt}')
            sales_agent = sales_agent_manager.get_sales_agent(user_id)
            sales_agent.human_step(user_promt)
            sales_agent.determine_conversation_stage()
            ai_answer = sales_agent.step()
            print(ai_answer)
            create_ai_msg(user, ai_answer, 'Guru')
            answer = (f'{user_promt}')
            print(f'ai answer:{ai_answer}')
            print(answer)
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
            try:
                subprocess.run(
                    ['ffmpeg', '-i', str(filename), '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16k',
                     str(wav_filename)],
                    check=True)
                
                user_promt = utils.speech_to_text(str(wav_filename))
                print('WHISPER RUUUUUUUUUUN')
                create_user_msg(user, user_promt)
                utils.write_to_history(user_id, user_name, user_promt)
                print('DB UPDATED')
                sales_agent = sales_agent_manager.get_sales_agent(user_id)
                sales_agent.human_step(user_promt)
                sales_agent.determine_conversation_stage()
                ai_answer = sales_agent.step()
                print(f'ai answer:{ai_answer}')
                print('succ utils')
                create_ai_msg(user, ai_answer, 'Guru')
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running ffmpeg: {e}")
            finally:
                print('trying to delete')
                try:
                    os.remove(filename)
                    os.remove(wav_filename)
                    logger.info(f"Files {filename} and {wav_filename} deleted.")
                except Exception as e:
                    logger.error(f"Error deleting files: {e}")
        
        ai_answer = utils.check_dialogue_end_and_print_summary(user_id, ai_answer, user_promt)
        utils.write_to_history_assistant(user_id, ai_answer)
        GPTbot.reply_to(message=message, text=ai_answer)
        ai_answer = check_photo_code(GPTbot, chat_id, ai_answer, user_promt)    
        message_queue.task_done()
        print('mesage task done')



def is_waiting_for_response(user_id):
    return user_id in message_status and message_status[user_id]['waiting_for_response']


@GPTbot.message_handler(commands=["start"])
def start_command_handler(message: callable) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    accounts_dir = os.path.join(ACCOUNTS_DIR, str(user_id))
    if not os.path.exists(accounts_dir):
        os.makedirs(accounts_dir)
    history_file_path = os.path.join(accounts_dir, 'history.txt')
    with open(history_file_path, 'w+') as file:
        # This step is optional, it clears the file if it already exists
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