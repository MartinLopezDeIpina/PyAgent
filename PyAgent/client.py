import asyncio
import os
import pdb
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

SERVER_IP = os.environ.get("SERVER_IP")
SERVER_PORT = os.environ.get("SERVER_PORT")

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self):
        print("Connecting to server...")

        streams = await self.exit_stack.enter_async_context(
            sse_client(f"http://{SERVER_IP}:{SERVER_PORT}/sse")
        )

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(streams[0], streams[1])
        )

        await self.session.initialize()
        print("Session initialized")

        response = await self.session.list_tools()
        print(f"respuesta: {response}")
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def call_tool(self, tool_name, tool_args):
        result = await self.session.call_tool(tool_name, tool_args)

        return result


async def main():
    client = MCPClient()

    try:
        await client.connect_to_server()

        tool_name = "rag_stackoverflow_posts_tool"
        tool_args = {
            "query": "how to sort a list in python"
        }

        result = await client.call_tool(tool_name, tool_args)
        print(result)

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())