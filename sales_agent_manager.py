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
        sales_agent = SalesGPT.from_llm(llm, use_tools=True, verbose=False,
                                        product_catalog="examples/sample_product_catalog.txt",
                                        schedule_file="examples/schedule.txt",
                                        salesperson_name="Miki",
                                        salesperson_role="Виртуальный администратор",
                                        company_name="Ресторан Miki",
                                        company_business='''Ресторан Miki
                                    располагается на первом этаже гостиницы Hotel Kirov,
                                    всех желающих мы приглашаем в ресторан - только у нас вы можете попробовать
                                    вкуснейшие блюда европейской и греческой кухни, время работы ресторана - ежедневно с 12:00 до 24:00.''',
                                        company_values='Дать людям очень вкусную еду',
                                        conversation_type='chat',
                                        conversation_purpose='Забронировать столик для клиента, получи дату и время записи, имя и номер телефона',
                                        )
        sales_agent.seed_agent()
        return sales_agent

    def get_sales_agent(self, user_id):
        if user_id not in self.agents:
            self.agents[user_id] = self.initialize_sales_agent(user_id)
        return self.agents[user_id]

