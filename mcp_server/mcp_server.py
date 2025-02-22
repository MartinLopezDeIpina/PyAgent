from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
import uvicorn
from mcp.server.lowlevel import Server
import requests
from mcp import types
from mcp.cli import app
from tools import rag_stackoverflow_posts_tool, rag_docs_tool


TOOLS_APP_URL = "http://localhost:5000"

mcp = FastMCP("acciones")

if __name__ == "__main__":
    # Initialize and run the server
    print("runeado server")

    app = Server("python_tools")
    sse = SseServerTransport("/messages/")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        print(f"Calling tool {name} with arguments {arguments}")

        if name == "rag_stackoverflow_posts_tool":
            return rag_stackoverflow_posts_tool(arguments)
        elif name == "rag_docs_tool":
            return rag_docs_tool(arguments)
        else:
            return {
                "status": 404,
                "error": "function not found"
            }

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="rag_stackoverflow_posts_tool",
                description="Fetches stackoverflow posts for a given query",
                inputSchema={
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                    }
                }
            ),
            types.Tool(
                name="rag_docs_tool",
                description="Fetches docs for a given library and query",
                inputSchema={
                    "type": "object",
                    "required": ["library", "query"],
                    "properties": {
                        "library": {"type": "string"},
                        "query": {"type": "string"},
                    }
                }
            )
        ]

    async def handle_sse(request):
        async with sse.connect_sse(
                request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)
