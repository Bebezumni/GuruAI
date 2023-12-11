from langchain.llms import OpenAI
from llama_index import (
    SimpleDirectoryReader, GPTVectorStoreIndex,
    LLMPredictor, PromptHelper, ServiceContext
)
import openai
import os
import utils
# Set up the OpenAI API key
openai.api_key = utils.openai_api_key

# Set up the OpenAI API key as an environment variable
os.environ['OPENAI_API_KEY'] = openai.api_key

# Load training data from a directory named "datos"
docs = SimpleDirectoryReader("datos").load_data()

# Define parameters
max_input = 4098
tokens = 256
chnk_size = 600
max_chnk_overlap = 0.2


def entrenamiento(path):
    """
    Train a GPTVectorStore index using documents in the specified directory.

    Args:
        path (str): Path to the directory containing training data.

    Returns:
        None
    """
    Prompt_helper = PromptHelper(
        max_input,
        tokens,
        max_chnk_overlap,
        chunk_size_limit=chnk_size
    )

    modelo = LLMPredictor(llm=OpenAI(
        temperature=0,
        model_name="text-ada-001",
        max_tokens=tokens
        )
    )

    contexto = ServiceContext.from_defaults(
        llm_predictor=modelo,
        prompt_helper=Prompt_helper
    )

    index_model = GPTVectorStoreIndex.from_documents(
        docs,
        service_context=contexto
    )

    index_model.storage_context.persist(persist_dir='Modelo')


#  Call the training function with the "datos" directory
entrenamiento("datos")
