from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config.settings import OLLAMA_MODEL, OLLAMA_BASE_URL

template = """
You are an AI assistant specialized in generating SQL queries.

Database schema:
{schema}

Generate a correct, optimized SQL query for the following user request.
Return ONLY the SQL query.

User request:
{question}
"""

llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
prompt = PromptTemplate(input_variables=["schema", "question"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)
