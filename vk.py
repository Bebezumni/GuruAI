import dotenv
dotenv.load_dotenv()
import vk_api
import django
django.setup()
import utils
import os
from vk_api.longpoll import VkLongPoll, VkEventType
from sales_agent_manager import SalesAgentManager
from apps.home.models import ChatUser, UserMessage, AiAnswer
from objects_creator import create_user_msg, create_ai_msg

vk_session = vk_api.VkApi(token="vk1.a.5Xd_NDBmW8a2c8hT7mko3m02rU7u_s_LtSDuAHSkVhyp8sJIULuUqE3qkKbJh-KQwjYhR9JAWwx9_Ychesk7L4EnvERmFp9bk31yOlwWjnjNr4YwZ67XgbSxjpgCrBP9D9RzmClKXP6jIgxv6Og9dDwUERaURoIVnjKemWuxpSRM28ILNELD8bQqc9RPs3UZFNaEX6y8NthwAZUMglU_kQ")
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)
sales_agent_manager = SalesAgentManager()
ACCOUNTS_DIR = "Accounts"
RECORDINGS_DIR = "recordings"
def send_msg(id,text):
    vk_session.method("messages.send", {"user_id":id, "message":text,"random_id":0})


print('VK BOT IS ONLINE')
for event in longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:


            message = event.text.lower()
            id = event.user_id
            user, created = ChatUser.objects.get_or_create(user_name=id, user_id=id, messenger='VK')
            create_user_msg(user, message)
            accounts_dir = os.path.join(ACCOUNTS_DIR, str(id))
            if not os.path.exists(accounts_dir):
                os.makedirs(accounts_dir)
            history_file_path = os.path.join(accounts_dir, 'history.txt')
            with open(history_file_path, 'a') as file:
                file.close()
            utils.write_to_history(id, id, message)
            sales_agent = sales_agent_manager.get_sales_agent(id)
            sales_agent.human_step(message)
            sales_agent.determine_conversation_stage()

            ai_answer = sales_agent.step()
            utils.write_to_history_assistant(id, ai_answer)
            ai_answer = utils.check_dialogue_end_and_print_summary(id, ai_answer, message)
            create_ai_msg(user, ai_answer, 'Guru')
            send_msg(id,ai_answer)
