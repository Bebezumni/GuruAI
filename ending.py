import re

import requests

from historyparser import parse_dialogue, parse_dialogue_to_summary
from openai import OpenAI
import utils
import unittest

client = OpenAI(api_key="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")


def get_content_after_second_last_dialogue_end(text):
    # Find all occurrences of <DIALOGUE_END>
    dialogue_end_matches = re.finditer(r'<END_OF_CALL>', text)

    # Find the positions of the second-to-last and last occurrences
    positions = [match.start() for match in dialogue_end_matches]
    if len(positions) == 1:
        return text[:positions[0]].strip()
    elif len(positions) < 2:
        return text

    second_last_position = positions[-2]

    # Extract content between the second-to-last and last occurrences
    content_after_second_last = text[second_last_position + len('<END_OF_CALL>'):positions[-1]].strip()

    return content_after_second_last

def parse_response(response):
    # Split the response by commas
    values = response.split(',')
    print(f'ДЛИНА ПЕРСЕРА КОНЦА ДИАЛОГА:\n{len(values)}')

    if len(values) == 4:
        # Extract values and remove leading/trailing spaces
        user_id = values[0].strip().split(':')[1].strip()
        name = values[1].strip().split(':')[1].strip()
        phone_number = values[2].strip().split(':')[1].strip()
        dialogue_summary = values[3].strip().split(':')[1].strip()
        # You can print or return the extracted information
        print(f"User ID: {user_id}")
        print(f"Name: {name}")
        print(f"Phone Number: {phone_number}")
        print(f'Summary {dialogue_summary}')
        b24url = f"https://guruai.bitrix24.ru/rest/1/0u5kbm63tiosg3hd/crm.lead.add.json?FIELDS[TITLE]={dialogue_summary}&FIELDS[NAME]={name}&FIELDS[LAST_NAME]={name}&FIELDS[PHONE][0][VALUE]={phone_number}&FIELDS[PHONE][0][VALUE_TYPE]=WORK"

        req = requests.post(url=b24url)
        print('BITRIX REQ SENT')
        # If you want to save the information to variables, you can return them
        return user_id, name, phone_number, dialogue_summary

    else:
        print("Unexpected format in the response.")
        return None

def get_summary(user_id, promt):
    try:
        with open(f'Accounts/{user_id}/history.txt', 'r', encoding='UTF-8') as file:
            content = file.read()
            # content_after_second_last = get_content_after_second_last_dialogue_end(content)
            print(f'КОНТЕНТ НА ПОДВЕДЕНИЕ ИТОГОВ:\n{content}')
            content = parse_dialogue_to_summary(content)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=content,
            )
            with open(f'Accounts/{user_id}/history.txt', 'w', encoding='UTF-8') as file:
                file.write(f'ИТОГИ НАШЕГО ПРОШЛОГО ДИАЛОГА:{completion.choices[0].message.content}')
            
            with open(f'Accounts/{user_id}/history_full.txt', 'a', encoding='UTF-8') as file:
                file.write(f'ИТОГИ НАШЕГО ПРОШЛОГО ДИАЛОГА:{completion.choices[0].message.content}')
            return completion.choices[0].message.content



    except FileNotFoundError:
        print(f"History file not found for user {user_id}")
        return []


