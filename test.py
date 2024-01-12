import requests
import json
import os
from dotenv import load_dotenv

dotenv_path = os.path.join('', '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()

tok = os.getenv("AMOCRM_ACCESS_TOKEN")

access_token = "Bearer " + tok
headers = {"Authorization": access_token}
def send_example_request():
    url = "https://aamcorporation.amocrm.ru/api/v4/leads"  # Replace with the actual API endpoint URL

    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": access_token # Replace with the actual access token if required
    # }

    example_request = [
        {
            "pipeline_id": 7608438,
            "name": 'Арсений оставил заявку на подтверждение встречи',
            'custom_fields_values': [
                {
                    "field_id": 1425989,
                    "values": [
                        {
                            "value": 'ИНФОРМАЦИЯ'
                        }
                    ]
                },
            ]
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

send_example_request()