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
from apps.home.models import ChatMessage, ChatUser

app = Flask(__name__)
sales_agent_manager = SalesAgentManager()
ACCOUNTS_DIR = "Accounts"
RECORDINGS_DIR = "recordings"

# OpenAi API key
openai.api_key = utils.openai_api_key
print(utils.openai_api_key)
# Access token for your WhatsApp business account app
whatsapp_token = utils.WHATSAPP_TOKEN
print(os.environ.get("WHATSAPP_TOKEN"))
WHATSAPP_BUSINESS_ACCOUNT_ID = utils.WHATSAPP_BUSINESS_ACCOUNT_ID
# Verify Token defined when configuring the webhook
verify_token = utils.VERIFY_TOKEN
print(os.environ.get("VERIFY_TOKEN"))
# Message log dictionary to enable conversation over multiple messages
message_log_dict = {}

LANGUGAGE = "ru-RU"

# get the media url from the media id
def get_media_url(media_id):
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }
    url = f"https://graph.facebook.com/v18.0/{media_id}/"
    response = requests.get(url, headers=headers)
    print(f"media id response: {response.json()}")
    return response.json()["url"]

@app.route('/subscribe_whatsapp', methods=['POST'])
def subscribe_whatsapp():
    url = f'https://graph.facebook.com/v18.0/{WHATSAPP_BUSINESS_ACCOUNT_ID}/subscribed_apps'
    headers = {
        'Authorization': f'Bearer {whatsapp_token}',
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": "Subscribed to WhatsApp Business API successfully!"}), 200
    else:
        error_message = f"Failed to subscribe to WhatsApp Business API. Status Code: {response.status_code}, Response: {response.text}"
        return jsonify({"error": error_message}), 500


# download the media file from the media url
def download_media_file(media_url):
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }
    response = requests.get(media_url, headers=headers)
    print(f"first 10 digits of the media file: {response.content[:10]}")
    return response.content


# convert ogg audio bytes to audio data which speechrecognition library can process
def convert_audio_bytes(audio_bytes):
    ogg_audio = pydub.AudioSegment.from_ogg(io.BytesIO(audio_bytes))
    ogg_audio = ogg_audio.set_sample_width(4)
    wav_bytes = ogg_audio.export(format="wav").read()
    audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="int32")
    sample_width = audio_data.dtype.itemsize
    print(f"audio sample_rate:{sample_rate}, sample_width:{sample_width}")
    audio = sr.AudioData(audio_data, sample_rate, sample_width)
    return audio


# run speech recognition on the audio data
def recognize_audio(audio_bytes):
    recognizer = sr.Recognizer()
    audio_text = recognizer.recognize_google(audio_bytes, language=LANGUGAGE)
    return audio_text


# handle audio messages
def handle_audio_message(audio_id):
    audio_url = get_media_url(audio_id)
    audio_bytes = download_media_file(audio_url)
    audio_data = convert_audio_bytes(audio_bytes)
    audio_text = recognize_audio(audio_data)
    return audio_text


# send the response as a WhatsApp message back to the user
def send_whatsapp_message(body, message):
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    url = "https://graph.facebook.com/v18.0/" + phone_number_id + "/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"whatsapp message response: {response.json()}")
    response.raise_for_status()

def send_instagram_message(body, response):
    # Send the response back to the Instagram user
    # You can customize this part based on how you interact with the Instagram API
    recipient_id = body["entry"][0]["messaging"][0]["sender"]["id"]

    # Assuming you have a function to send a message through the Instagram API
    send_message_to_instagram_api(recipient_id, response)

# create a message log for each phone number and return the current message log
def update_message_log(message, phone_number, role):
    initial_log = {
        "role": "system",
        "content": "You are a helpful assistant named WhatsBot.",
    }
    if phone_number not in message_log_dict:
        message_log_dict[phone_number] = [initial_log]
    message_log = {"role": role, "content": message}
    message_log_dict[phone_number].append(message_log)
    return message_log_dict[phone_number]


# remove last message from log if OpenAI request fails
def remove_last_message_from_log(phone_number):
    message_log_dict[phone_number].pop()


# make request to OpenAI
def make_openai_request(message, from_number):
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
    user, created = ChatUser.objects.get_or_create(user_name=from_number, user_id=from_number, messenger='Insta/whatsapp')
    create_user_msg(user, message)
    ai_answer = sales_agent.step()
    utils.write_to_history_assistant(from_number, ai_answer)
    ai_answer = utils.check_dialogue_end_and_print_summary(from_number, ai_answer, message)
    create_ai_msg(user, ai_answer)
    return ai_answer

# handle WhatsApp messages of different type
def handle_whatsapp_message(body):
    print('MESSAGE DETECTED in WHM')
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
    elif message["type"] == "audio":
        audio_id = message["audio"]["id"]
        message_body = handle_audio_message(audio_id)
    response = make_openai_request(message_body, message["from"])
    send_whatsapp_message(body, response)

def handle_instagram_message(body):
    # Handle Instagram message logic here
    # You can access Instagram message details from the 'body' parameter
    # For example, to get the random_text from Instagram message

    random_text = body["entry"][0]["messaging"][0]["message"]["text"]
    response = make_openai_request(random_text, body["entry"][0]["messaging"][0]["sender"]["id"])
    print(f"Random text from Instagram: {random_text}")
    send_message_to_instagram_api(body["entry"][0]["messaging"][0]["sender"]["id"], response)


# handle incoming webhook messages
def handle_message(request):
    print(f'request full:{request}')
    # Parse Request body in json format
    print('MESSAGE DETECTED')
    body = request.get_json()
    print(f"request body: {body}")

    try:
        if body.get("object") == "whatsapp_business_account":
            # Handle WhatsApp message
            if (
                body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
                and body["entry"][0]["changes"][0]["value"]["messages"][0]
            ):
                handle_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200

        elif body.get("object") == "instagram":
            # Handle Instagram message
            if (
                body.get("entry")
                and body["entry"][0].get("messaging")
                and body["entry"][0]["messaging"][0].get("message")
                and body["entry"][0]["messaging"][0]["message"].get("text")
            ):
                handle_instagram_message(body)
            return jsonify({"status": "ok"}), 200

        else:
            # If the request is not a supported platform, return an error
            return (
                jsonify({"status": "error", "message": "Unsupported messaging platform"}),
                404,
            )

    # Catch all other errors and return an internal server error
    except Exception as e:
        print(f"unknown error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Required webhook verifictaion for WhatsApp
# info on verification request payload:
# https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests
def verify(request):
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == verify_token:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


# Sets homepage endpoint and welcome message
@app.route("/", methods=["GET"])
def home():
    return "Webhook is listening!"


# Accepts POST and GET requests at /webhook endpoint
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return verify(request)
    elif request.method == "POST":
        return handle_message(request)

@app.route("/webhook_insta", methods=["POST", "GET"])
def webhook_insta():
    if request.method == "GET":
        return verify(request)
    elif request.method == "POST":
        return handle_message(request)


# Route to reset message log
@app.route("/reset", methods=["GET"])
def reset():
    global message_log_dict
    message_log_dict = {}
    return "Message log resetted!"
if __name__ == "__main__":
    ssl_cert_path = "/etc/letsencrypt/live/guruai.store/fullchain.pem"
    ssl_key_path = "/etc/letsencrypt/live/guruai.store/privkey.pem"

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_cert_path, ssl_key_path)
    app.run(debug=True, use_reloader=True, host='0.0.0.0', ssl_context=ssl_context)
