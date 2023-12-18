import dotenv
from dotenv import dotenv_values
import logging
config = dotenv_values(".env")
print(config)
dotenv.load_dotenv()
import telebot
import utils
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


def process_messages():
    while True:
        message = message_queue.get()
        GPTbot.send_chat_action(chat_id=message.chat.id, action="typing")
        print('message started to process')
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        user, created = ChatUser.objects.get_or_create(user_name=user_name, user_id=user_id, messenger='Telegram')
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
            utils.write_to_history_assistant(user_id, ai_answer)
            ai_answer = utils.check_dialogue_end_and_print_summary(user_id, ai_answer, user_promt)    
            answer = (f'{user_promt}')
            print(f'ai answer:{ai_answer}')
            print(answer)
            if ai_answer:
                GPTbot.reply_to(message=message, text=ai_answer)
            else:
                print("Error: ai_answer is empty. Check your message generation logic.")
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
                ai_answer = utils.check_dialogue_end_and_print_summary(user_id, ai_answer, user_promt)
                utils.write_to_history_assistant(user_id, ai_answer)
                print('succ utils')
                GPTbot.reply_to(message=message, text=ai_answer)
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
    user, created = ChatUser.objects.get_or_create(user_name=user_name, user_id=user_id)
    create_ai_msg(user, ai_answer)
@GPTbot.message_handler(content_types=["text", "voice"])
def handle_text(message):
    message_queue.put(message)


if __name__ == "__main__":
    try:
        threading.Thread(target=process_messages, daemon=True).start()
        GPTbot.infinity_polling(skip_pending=True, none_stop=True)
        print('bot polling started')
    except:
        print("Lost connection!")