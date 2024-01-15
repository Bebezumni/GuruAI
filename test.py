import requests
import json
import os
from dotenv import load_dotenv
import time
dotenv_path = os.path.join('', '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()

def send_amo_lead():
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
                    "name": 'USER оставил заявку на подтверждение встречи',
                    # 'custom_fields_values': [
                    #     {
                    #         "field_id": 1425989,
                    #         "values": [
                    #             {
                    #                 "value": 'ИНФОРМАЦИЯ'
                    #             }
                    #         ]
                    #     }
                    # ]
                }],
                'contacts':[{
                    "first_name": 'USER_NAME',
                    "custom_fields_values":[
                        {
                        "field_id": 1757935,
                        "values": [
                            {
                                "value": "ИНФО ТУТ?"
                            }
                        ]
                        },
                        {
                        "field_id": 1414653,
                        "values": [
                            {
                                "value": "+79999991111"
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

send_amo_lead()