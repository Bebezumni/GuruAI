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
        sales_agent = SalesGPT.from_llm(llm, use_tools=False,
                                        verbose=True,
                                        product_catalog="examples/sample_product_catalog.txt",
                                        schedule_file="examples/schedule.txt",
                                        salesperson_name='Guru',
                                        salesperson_role="Виртуальный администратор",
                                        company_name="Компания All-Line",
                                        company_business='''Компания предоставляет услуги высокоскоростного доступа в интернет и цифрового телевидения в городах Алматы, Астаны. ''',
                                        company_values='Предоставлять бесперебойный доступ в интернет для своих клиентов, повышать надёжность канала связи, развиваться на рынке телекоммуникаций',
                                        conversation_type='chat',
                                        conversation_purpose='Выявить потребность клиента в коммуникационных услугах, назначить звонок с менеджером для согласования даты и времени подключения',
                                        )
        sales_agent.seed_agent()
        return sales_agent

    def get_sales_agent(self, user_id):

        if user_id not in self.agents:
            print('NEW AGENT INITIALISING')
            self.agents[user_id] = self.initialize_sales_agent(user_id)
        return self.agents[user_id]

