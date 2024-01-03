import sys
import subprocess
import threading
import time
import signal

def start_chatbot():
    try:
        print("Starting Chatbot...")
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print("Chatbot thread interrupted")

def start_django_server():
    try:
        print("Starting Django Server...")
        subprocess.run([
  	  "python",
 	   "manage.py",
 	   "runsslserver",
 	   '194.180.188.182:8000',
 	   '--cert', '/etc/letsencrypt/live/insidemoney.guruai.space/fullchain.pem',
 	   '--key', '/etc/letsencrypt/live/insidemoney.guruai.space/privkey.pem'
	])  
    except KeyboardInterrupt:
        print("Django server thread interrupted")

def start_webhook_server():
    try:
        print("Starting Webhooks Server...")
        subprocess.run(["python", "app.py"])
    except KeyboardInterrupt:
        print("Webhooks server thread interrupted")

def start_vk_app():
    try:
        print('VK bot is starting....')
        subprocess.run(["python", "vk.py"])
    except KeyboardInterrupt:
        print("VK app thread interrupted")

def signal_handler(sig, frame):
    print("\nCtrl+C received. Stopping all threads.")
    sys.exit(0)

if __name__ == "__main__":
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Start the chatbot and Django server in separate threads
    chatbot_thread = threading.Thread(target=start_chatbot)
    django_thread = threading.Thread(target=start_django_server)
    webhook_thread = threading.Thread(target=start_webhook_server)
    vk_thread = threading.Thread(target=start_vk_app)

    try:
        django_thread.start()
        time.sleep(2)
        chatbot_thread.start()
        time.sleep(2)
        # webhook_thread.start()
        time.sleep(2)
        vk_thread.start()

        # Wait for both threads to finish
        chatbot_thread.join()
        django_thread.join()
        # webhook_thread.join()
        vk_thread.join()

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt. Stopping all threads.")
        sys.exit(0)