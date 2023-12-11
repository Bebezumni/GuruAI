
import sys
import subprocess
# venv_site_packages = r'C:\Users\Арсений\Desktop\GuruAI_0.9.3_web_new\webserver\venv\Lib\site-packages'
# additional_path = r'C:\Users\Арсений\Desktop\GuruAI_0.9.3_web_new\webserver\venv\Scripts\python.exe'
# sys.path = [venv_site_packages, additional_path]
#
print(sys.path)
import threading
import time
import sys

def start_chatbot():
    print("Starting Chatbot...")
    subprocess.run(["python", "main.py"])

def start_django_server():
    print("Starting Django Server...")
    subprocess.run(["python", "manage.py", "runserver"])

def start_webhook_server():
    print("Starting Webhooks Server...")
    subprocess.run(["python", "app.py"])

def start_vk_app():
    print('VK bot is starting....')
    subprocess.run(["python", "vk.py"])


if __name__ == "__main__":
    # Start the chatbot and Django server in separate threads
    chatbot_thread = threading.Thread(target=start_chatbot)
    django_thread = threading.Thread(target=start_django_server)
    webhook_thread = threading.Thread(target=start_webhook_server)
    vk_thread = threading.Thread(target=start_vk_app)
    django_thread.start()
    time.sleep(2)
    chatbot_thread.start()
    time.sleep(2)  # Give some time for the chatbot to initialize, adjust as needed
    # webhook_thread.start()
    time.sleep(2)
    vk_thread.start()
    # Wait for both threads to finish (you can also add a KeyboardInterrupt handling here)
    chatbot_thread.join()
    django_thread.join()
    # webhook_thread.join()
    vk_thread.join()