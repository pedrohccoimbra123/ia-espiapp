from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_ollama import ChatOllama
import json

# FastAPI app
app = FastAPI()

# Carregar os dados locais
with open("local_data.json", "r", encoding="utf-8") as file:
    items = json.load(file)

# Função auxiliar para formatar locais
def formatar_locais(items):
    return "\n".join(
        f"{i}. {item['title']} - {item['description']} {item['imageText']}"
        for i, item in enumerate(items, 1)
    )

# Modelo de entrada da requisição
class QueryRequest(BaseModel):
    user_query: str

# Modelo Pydantic de saída estruturada
class LocalMatch(BaseModel):
    numero_identificador: int = Field(..., description="Número do local que melhor corresponde ao interesse do usuário")

# Output parser
parser = PydanticOutputParser(pydantic_object=LocalMatch)

# Template com instruções claras
template = """
Considere os seguintes locais em Belém. Qual deles melhor corresponde ao que o usuário está procurando?

Responda SOMENTE no seguinte formato JSON:
{format_instructions}

Locais disponíveis:
{locais}

O usuário diz: '{user_query}'
"""

# Prompt com instruções embutidas
prompt = PromptTemplate.from_template(template).partial(
    format_instructions=parser.get_format_instructions()
)

# LLM local
llm = ChatOllama(model="llama3")

# Chain com LangChain
chain: Runnable = prompt | llm | parser

# Rota da API
@app.post("/match")
def match_location(request: QueryRequest):
    try:
        locais = formatar_locais(items)
        result = chain.invoke({"user_query": request.user_query, "locais": locais})
        return {"numero_identificador": result.numero_identificador}
    except Exception as e:
        return {"error": str(e)}
