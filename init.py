
import utils
import telebot
from telebot import types

# Connect to bot
# Token placed in utils.py file. You can change it with your token
GPTbot = telebot.TeleBot(utils.Token)
print(f"The Bot is online (id: {GPTbot.get_me().id}) \33[0;31m[DEVELOPER MODE]\33[m...")

# Set bot commands
print("[!] Configuring bot commands...")
GPTbot.set_my_commands(
    commands=[
        types.BotCommand(
            command="start",
            description="Начать"
        ),
    ]
)
print("[!] Commands successfully configured.\n[!] Run main.py")
