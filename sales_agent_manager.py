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
                                        salesperson_role="Инвестиционный консультант",
                                        company_name="Inside Money",
                                        company_business='''Компания Inside Money - строит новую долину стартапов с развитой экосистемой в сердце Бали,Мы предлагаем инвестиции в коммерческую недвижимость с высокой окупаемостью''',
                                        company_values='Создание высокодоходных инвестиционных условий в коммерческую недвижимость на Бали для наших клиентов ',
                                        conversation_type='chat',
                                        conversation_purpose='узнать что мы за компания, узнать какие мы услуги предоставляем, узнать сколько он может заработать на инвестициях в коммерческую недвижимость на Бали, записаться на zoom встречу с руководителем отдела продаж Евгением Барабаш, дать свой номер телефона и имя',
                                        )
        sales_agent.seed_agent()
        return sales_agent

    def get_sales_agent(self, user_id):

        if user_id not in self.agents:
            print('NEW AGENT INITIALISING')
            self.agents[user_id] = self.initialize_sales_agent(user_id)
        return self.agents[user_id]

