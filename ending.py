import re
import platform
import requests
import os
from historyparser import parse_dialogue, parse_dialogue_to_summary
from openai import OpenAI
import utils
import unittest
import time
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

def parse_response(response, crm):
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
        if crm == 'bitrix':
            b24url = f"https://guruai.bitrix24.ru/rest/1/0u5kbm63tiosg3hd/crm.lead.add.json?FIELDS[TITLE]={dialogue_summary}&FIELDS[NAME]={name}&FIELDS[LAST_NAME]={name}&FIELDS[PHONE][0][VALUE]={phone_number}&FIELDS[PHONE][0][VALUE_TYPE]=WORK"

            req = requests.post(url=b24url)
            print('BITRIX REQ SENT')
            # If you want to save the information to variables, you can return them
            return user_id, name, phone_number, dialogue_summary
        else:
            send_amo_lead(name, dialogue_summary, phone_number)
            print('Amo lead sent')

    else:
        if crm == 'bitrix':
            print('format is unknown trying to send lead')
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
            user_id = values[0].strip().split(':')[1].strip()
            name = values[1].strip().split(':')[1].strip()
            phone_number = values[2].strip().split(':')[1].strip()
            dialogue_summary = values[3].strip().split(':')[1].strip()
            # You can print or return the extracted information
            print(f"User ID: {user_id}")
            print(f"Name: {name}")
            print(f"Phone Number: {phone_number}")
            print(f'Summary {dialogue_summary}')
            send_amo_lead(name, dialogue_summary, phone_number)
def send_amo_lead(user_name, dialogue_results, phone):
    url = "https://aamcorporation.amocrm.ru/api/v4/leads/unsorted/forms"
    tok = os.getenv("AMOCRM_ACCESS_TOKEN")
    access_token = "Bearer " + tok
    headers = {"Authorization": access_token}
    example_request = [
        {
            "source_uid": '12345',
            "source_name": 'GuruAI Bot Lead',
            "pipeline_id": 7608438,
            "_embedded": {
                'leads': [{
                    "name": f'{user_name} оставил заявку на подтверждение встречи',
                }],
                'contacts':[{
                    "first_name": user_name,
                    "custom_fields_values":[
                        {
                        "field_id": 1757935,
                        "values": [
                            {
                                "value": dialogue_results
                            }
                        ]
                        },
                        {
                        "field_id": 1414653,
                        "values": [
                            {
                                "value": phone
                            }
                        ]
                        },
                    ]
                }]
            },
            "metadata": {
                "ip": '0.0.0.0',
                "form_id": "1263594",
                "form_sent_at": int(time.time()),
                "form_name": 'guru form',
                "form_page": 'Lead от GuruAI',
                "referer": "https://guruai.space"
            },
        }

    ]
    try:
        print(f'headers:\n{headers}')
        print(f'body:\n{example_request}')
        response = requests.post(url, headers=headers, json=example_request)
        print(response.json())
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print("Request sent successfully!")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error sending request:", e)

def get_encoding():
    system = platform.system()
    print(system)
    return 'cp1251' if system == 'Windows' else 'UTF-8'
def get_summary(user_id, promt):
    encoding = get_encoding()
    try:
        with open(f'Accounts/{user_id}/history.txt', 'r', encoding=encoding) as file:
            content = file.read()
            print(f'КОНТЕНТ НА ПОДВЕДЕНИЕ ИТОГОВ:\n{content}')
            content = parse_dialogue_to_summary(content)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=content,
            )
            with open(f'Accounts/{user_id}/history.txt', 'w', encoding=encoding) as file:
                file.write(f'ИТОГИ НАШЕГО ПРОШЛОГО ДИАЛОГА:{completion.choices[0].message.content}')

            with open(f'Accounts/{user_id}/history_full.txt', 'a', encoding=encoding) as file:
                file.write(f'ИТОГИ НАШЕГО ПРОШЛОГО ДИАЛОГА:{completion.choices[0].message.content}')
            return completion.choices[0].message.content



    except FileNotFoundError:
        print(f"History file not found for user {user_id}")
        return []


