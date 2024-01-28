import whisper
import openai
import ending
import json
import os
import platform
# import time
from llama_index import StorageContext, load_index_from_storage
Token = "6870166258:AAELKQ0QNJIS1_IdI3Ixus5QKVFXNfpHaAA"
openai_api_key = "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"
WHATSAPP_BUSINESS_ACCOUNT_ID = "168724609661438"
VERIFY_TOKEN='GURUTOKEN'
WHATSAPP_TOKEN='EAANfmCTCQNsBO6NYe1ZBiZB6QVMsZAGAKn4x7lmgCRyZCzJx2b6CtbWqcfIlKgO0ZADCd06H8tBr2deHfzW2AJoqVtHBpoiiCyWwZAIimT492p433JodW7ePfPlHekc1dZCgZA9paZCXGmwPC4XUoZAWbXPZCPVOZClHk99ZC81SjQn0pY9cOaC6KuwQCCRcjZCz2TgfnZCvugOpbKFWPJnRcAeTGTZBOs86FsvyHfCE4xE5utr7regh'
openai.api_key = openai_api_key
wh_model = whisper.load_model("base")
crm = 'bitrix'
ca_atoken= '59384cd3436c99ed2d7aa0d65b1fb66e0a08804c288d31f3b90f69277ee2e001'
ca_rtoken= '7811118d576b79caa7dbfae165d871e568c42463f5785342e0d7fa8efadb38fa'
def chatbot(question):
        """
        Отвечает на вопрос с использованием ранее обученного индекса.
    
        Args:
            question (str): Вопрос, введенный пользователем.
    
        Returns:
            str: Ответ, сгенерированный чатботом.
    
        """
        storage_context = StorageContext.from_defaults(persist_dir='Modelo')
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        response = query_engine.query(question)
        emb_response = (f'Ответ базы:{response}')
        print(emb_response)
        return response


def speech_to_text(audio_data) -> str:
    converted_text = wh_model.transcribe(audio_data, language='ru')
    text_value = converted_text['text']
    return text_value

def check_dialogue_end_and_print_summary(user_id, assistant_response, promt, crm):
    if crm == 'amo':
        if '<END_OF_CALL>' in assistant_response:
            print('dialogue end detected for amo crm')
            assistant_response = assistant_response.replace('<END_OF_CALL>', '')
            summary = ending.get_summary(user_id, promt)
            print(f'ИТОГИ ДИАЛОГА:\n {summary}')
            ending.parse_response(summary, crm)

    else:
        if '<END_OF_CALL>' in assistant_response:
            print('dialogue end detected')

            # Print the original response
            print(f'Original response: {assistant_response}')

            # Replace <DIALOGUE_END> with an empty string
            assistant_response = assistant_response.replace('<END_OF_CALL>', '')

            # Print the modified response
            print(f'Modified response: {assistant_response}')

            summary = ending.get_summary(user_id, promt)
            print(f'ИТОГИ ДИАЛОГА:\n {summary}')
            ending.parse_response(summary, crm)
    return assistant_response

def write_to_history(user_id, user_name, text):
    directory = f'Accounts/{user_id}/'

    # Check if the directory exists, create it if not
    if not os.path.exists(directory):
        os.makedirs(directory)
        with open(os.path.join(directory, 'history.txt'), 'w+') as file:
            file.write(f'Created')
            # Now open the file for writing or creating
    with open(os.path.join(directory, 'history.txt'), 'a') as file:
        # Write your data to the file
        file.write(f'{user_name}: {text}\n')
        
    if not os.path.exists(directory):
        os.makedirs(directory)
        with open(os.path.join(directory, 'history_full.txt'), 'w+') as file:
            file.write(f'Created')
            # Now open the file for writing or creating
    with open(os.path.join(directory, 'history_full.txt'), 'a') as file:
        # Write your data to the file
        file.write(f'{user_name}: {text}\n')

def write_to_history_assistant(user_id, assistant_response):
    directory = f'Accounts/{user_id}/'

    # Check if the directory exists, create it if not
    if not os.path.exists(directory):
        os.makedirs(directory)
        with open(os.path.join(directory, 'history.txt'), 'w+') as file:
            file.write(f'Created')
            # Now open the file for writing or creating
    with open(os.path.join(directory, 'history.txt'), 'a') as file:
        # Write your data to the file
        file.write(f'Assistant: {assistant_response}\n')
        
    if not os.path.exists(directory):
        os.makedirs(directory)
        with open(os.path.join(directory, 'history_full.txt'), 'w+') as file:
            file.write(f'Created')
            # Now open the file for writing or creating
    with open(os.path.join(directory, 'history_full.txt'), 'a') as file:
        # Write your data to the file
        file.write(f'Assistant: {assistant_response}\n')
        
def save_thread_id(user_id, thread_id):
    try:
        with open('thread_data.json', 'r+') as file:
            try:
                thread_data = json.load(file)
            except json.JSONDecodeError:
                print("Error: Unable to decode JSON. Creating a new one.")
                thread_data = {}
            thread_data[str(user_id)] = thread_id
            file.seek(0)
            json.dump(thread_data, file, indent=4)
    except FileNotFoundError:
        print("Error: JSON file not found. Creating a new one.")
        with open('thread_data.json', 'w') as file:
            thread_data = {str(user_id): thread_id}
            json.dump(thread_data, file, indent=4)

def get_thread_id(user_id):
    try:
        with open('thread_data.json', 'r') as file:
            thread_data = json.load(file)
            print('thread_data.get(str(user_id))')
            return thread_data.get(str(user_id))
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Unable to decode JSON.")
        return None

image1='im1.jpg'
image2='im2.jpg'
image3='im3.jpg'
image4='im4.jpg'

def check_photo_code(GPTbot, chat_id, assistant_response, promt):
    if '<PHOTO_CODE>' in assistant_response:
        print('Photo code detected')
        assistant_response = assistant_response.replace('<PHOTO_CODE>', '')
        GPTbot.send_photo(chat_id, open(image1, 'rb'))
    return assistant_response
    
def check_bali_code(GPTbot, chat_id, assistant_response, promt):
    if '<BALI_CODE>' in assistant_response:
        print('Bali code detected')
        assistant_response = assistant_response.replace('<BALI_CODE>', '')
        GPTbot.send_photo(chat_id, open(image4, 'rb'))
    return assistant_response
    
def get_encoding():
    system = platform.system()
    print(system)
    return 'cp1251' if system == 'Windows' else 'UTF-8'

def count_tokens(file_path):
    encoding = get_encoding()
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            tokens = content.split()
        return len(tokens)
    except FileNotFoundError:
        print(f'File "{file_path}" not found. Skipping.')
        return 0

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('')  # Очищаем файл, записывая пустую строку
