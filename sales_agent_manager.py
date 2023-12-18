from copy import deepcopy
from salesgpt.tools import OpenAI
from salesgpt.agents import SalesGPT
from langchain.chat_models import ChatLiteLLM
from utils import openai_api_key
import os
os.environ['OPENAI_API_KEY'] = openai_api_key

class SalesAgentManager:
    def __init__(self):
        self.agents = {}

    def initialize_sales_agent(self, user_id):
        llm = ChatLiteLLM(temperature=0.4, model_name="gpt-3.5-turbo")
        sales_agent = SalesGPT.from_llm(llm, use_tools=True,
                                        verbose=False,
                                        product_catalog="examples/sample_product_catalog.txt",
                                        schedule_file="examples/schedule.txt",
                                        salesperson_name='Guru',
                                        salesperson_role="Виртуальный администратор",
                                        company_name="Компания GuRu AI",
                                        company_business='''Компания Guru AI Занимается разработка роботов с искусственным интеллектом для мессенджеров и социальных сетей''',
                                        company_values='Ценностное предложение GuRu AI заключается в предоставлении клиентам роботов с искусственным интеллектом, которые помогут им автоматизировать коммуникацию и повысить эффективность работы в мессенджерах и социальных сетях. Приложения для управления качеством, использующие аналитику, работают быстрее, точнее и объективнее, чем люди, и приносят больше ценности. Роботы GuRu AI помогут снизить нагрузку на сотрудников, сэкономить время и средства, а также повысить удовлетворенность клиентов.',
                                        conversation_type='chat',
                                        conversation_purpose='Назнавить встречу с с руководителем отдела продаж, на которой мы продемонстрируем как guru может улучшить работу, узнать его номер телефона и имя',
                                        )
        sales_agent.seed_agent()
        return sales_agent

    def get_sales_agent(self, user_id):

        if user_id not in self.agents:
            print('NEW AGENT INITIALISING')
            self.agents[user_id] = self.initialize_sales_agent(user_id)
        return self.agents[user_id]

