from langchain.agents import Tool
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


def setup_knowledge_base(product_catalog: str = None):
    """
    We assume that the product catalog is simply a text string.
    """
    # load product catalog
    with open(product_catalog, "r", encoding='utf-8') as f:
        product_catalog = f.read()

    text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    texts = text_splitter.split_text(product_catalog)

    llm = OpenAI(temperature=0)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(
        texts, embeddings, collection_name="product-knowledge-base"
    )

    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=docsearch.as_retriever()
    )
    return knowledge_base

def setup_schedule_knowledge_base(schedule_file: str = None):
    # Assuming your schedule file is a text string
    with open(schedule_file, "r", encoding='utf-8') as f:
        schedule_text = f.read()

    text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    schedule_texts = text_splitter.split_text(schedule_text)

    llm = OpenAI(temperature=0)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(
        schedule_texts, embeddings, collection_name="schedule-knowledge-base"
    )

    schedule = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=docsearch.as_retriever()
    )
    return schedule




def get_tools(knowledge_base, schedule):
    # we only use one tool for now, but this is highly extensible!
    tools = [
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            description="useful for when you need to answer questions about product information",
        ),
        Tool(
            name="ScheduleSearch",
            func=schedule.run,
            description="useful for when you need to set an appointment or search for available time slots in the schedule",
        )
    ]
    return tools

