import asyncio
import os
from openai import AzureOpenAI
from fastmcp import Client
from mcp.types import Tool

mcp_client = Client("http://localhost:8000/mcp")

endpoint = "https://eastus.api.cognitive.microsoft.com/"
model_name = "gpt-4.1"
deployment = "gpt-4.1"

subscription_key = ""
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

def convert_fastapi_to_openai_tools(tool_list: list) -> list:
    """
    Converts a list of Tool objects/dicts (like those from FastAPI/FastMCP) 
    into the format required by the Azure/OpenAI Chat Completions API.
    """
    openai_tools = []
    
    for mcp_tool in tool_list:
        if not isinstance(mcp_tool, Tool):
            print(f"Skipping invalid tool entry: {mcp_tool}")
            continue

        # # Check for essential fields
        # if 'name' not in tool_dict or 'inputSchema' not in tool_dict:
        #     print(f"Skipping tool due to missing 'name' or 'inputSchema': {tool_dict}")
        #     continue

        # Extracting and mapping fields
        tool_name = mcp_tool.name
        
        # Use the description if available, otherwise provide a fallback
        tool_description = "" if mcp_tool.description is None else mcp_tool.description
        
        tool_parameters = mcp_tool.inputSchema
        
        # Construct the Azure OpenAI tool schema entry
        openai_entry = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": tool_parameters
            }
        }
        openai_tools.append(openai_entry)
        
    return openai_tools

async def get_tools():
    async with mcp_client:
        tools = await mcp_client.list_tools()
        print("Tools:", len(tools))
        print("Tools:", tools)
        tool_specs = convert_fastapi_to_openai_tools(tools)
        print("Converted Tool Specs:", tool_specs)
        return tool_specs
        # tool_specs = [
        #     {
        #         "type": "function",
        #         "function": {
        #             "name": "get_current_weather",
        #             "description": "Get the current weather in a given location",
        #             "parameters": {
        #                 "type": "object",
        #                 "properties": {
        #                     "location": {
        #                         "type": "string",
        #                         "description": "The city and state, e.g., San Francisco, CA",
        #                     },
        #                     "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        #                 },
        #                 "required": ["location"],
        #             },
        #         },
        #     }
        # ]
        # return tool_specs



async def run():
    message_history = [{
        "role": "system",
        "content": "You are a helpful assistant.",
    }]
    message_history.append({
        "role": "user",
        "content": "What tools do you have?",
    })

    tool_specs = await get_tools()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        messages=message_history,
        max_completion_tokens=13107,
        temperature=1.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        model=deployment,
        tools=tool_specs, # Pass the tool schema here
    )

    print(response.choices[0].message.content)

async def main():
    async with mcp_client:
        # Basic server interaction
        await mcp_client.ping()
        
        # List available operations
        tools = await mcp_client.list_tools()
        print("Tools:", tools)
        # resources = await client.list_resources()
        # prompts = await client.list_prompts()
        
        # Execute operations
        # result = await client.call_tool("example_tool", {"param": "value"})
        # print(result)



if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(run())