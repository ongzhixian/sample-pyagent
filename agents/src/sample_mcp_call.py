import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

async def call_resource(name: str):
    async with client:
        content = await client.read_resource("resource://building/lights")
        print(content[0].text)

async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        # Execute operations
        result = await client.call_tool("example_tool", {"param": "value"})
        print(result)

        # Read a resource
        content = await client.read_resource("resource://building/lights")
        print(content[0].text)

if __name__ == "__main__":
    # Single calls for demonstration
    # asyncio.run(call_tool("Ford"))
    asyncio.run(call_resource("Ford"))
    # Run suite of examples
    # asyncio.run(main())