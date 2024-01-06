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
        llm = ChatLiteLLM(temperature=0.4, model_name="gpt-3.5-turbo", max_tokens=528)
        sales_agent = SalesGPT.from_llm(llm, use_tools=False,
                                        verbose=True,
                                        product_catalog="examples/sample_product_catalog.txt",
                                        schedule_file="examples/schedule.txt",
                                        salesperson_name='Guru',
                                        salesperson_role="Инвестиционный консультант",
                                        company_name="Inside Money",
                                        company_business='''Компания Inside Money - строит новую долину стартапов с развитой экосистемой в сердце Бали,мы предлагаем инвестиции в коммерческую недвижимость (офисы) с высокой окупаемостью и покупку коммерческой недвижимости (офисов) для личного использования разного метража и бюджета''',
                                        company_values='Создание высокодоходных инвестиционных условий в коммерческую недвижимость на Бали для своих партнеров и предоставление качественной офисной инфраструктуры для личного использования на продажу',
                                        conversation_type='chat',
                                        conversation_purpose='Рассказать о компании INSIDE MONEY, презентовать рынок Бали и рассказать он нем, познакомиться с клиентом, спросить чем он занимается и знаком ли он с рынком бали, позвать его на встречу и в случае интереа взять номер телефона',
                                        )
        sales_agent.seed_agent()
        return sales_agent

    def get_sales_agent(self, user_id):

        if user_id not in self.agents:
            print('NEW AGENT INITIALISING')
            self.agents[user_id] = self.initialize_sales_agent(user_id)
        return self.agents[user_id]

