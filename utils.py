import openai
import whisper
import openai
import ending
import json
import os
import asyncio
import datetime

# import time
from llama_index import StorageContext, load_index_from_storage
Token = 
openai_api_key = 
WHATSAPP_BUSINESS_ACCOUNT_ID = 
VERIFY_TOKEN=
WHATSAPP_TOKEN=
openai.api_key = openai_api_key
wh_model = whisper.load_model("base")

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

def check_dialogue_end_and_print_summary(user_id, assistant_response, promt):
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
        ending.parse_response(summary)
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
