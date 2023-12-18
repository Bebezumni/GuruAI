import dotenv
dotenv.load_dotenv()
import django
django.setup()
from apps.home.models import  ChatUser, UserMessage, AiAnswer

def create_user_msg(user, message_text):
    UserMessage.objects.create(user=user, message_text=message_text)

def create_ai_msg(user, response_text, ai_prefix):
    AiAnswer.objects.create(user=user, message_text=response_text, ai_prefix=ai_prefix)
