# FUNCTION TO GET TOOLS

async def get_tools(client):
    """Get tools from an already-connected MCP client."""
    return await client.list_tools()

def tool_to_openai(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema
        }
    }

async def call_tool_async(client, tool_name, arguments):
    """Async wrapper for tool calls."""
    return await client.call_tool(tool_name, arguments)