from mcp import types
from mcp.cli import app
import requests

TOOLS_APP_URL = "http://localhost:5000"

def rag_stackoverflow_posts_tool(arguments: dict):
    query = arguments["query"]

    URL = f"{TOOLS_APP_URL}/stackoverflow/rag_posts/{query}"
    response = requests.get(URL)
    response_json = response.json()

    return response_json

def rag_docs_tool(arguments: dict):
    library = arguments["library"]
    query = arguments["query"]

    URL = f"{TOOLS_APP_URL}/docs/doc_rag/{library}/{query}"
    response = requests.get(URL)
    response_json = response.json()

    return response_json
