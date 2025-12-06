import json
import os
from fastmcp import Client
from mcp.types import Tool

def get_secret(secret_key_id:str) -> str | None :
    sec_file_path = os.path.join(
        os.environ['APPDATA'],
        "Microsoft",
        "UserSecrets",
        "kairos",
        "pyagent-secrets.json")
    with open(sec_file_path, 'r', encoding='utf-8-sig') as data_file:
        data = json.load(data_file)
        if secret_key_id in data:
            return data[secret_key_id]
    return None


async def get_tools(*mcp_client_list: tuple[Client]):
    """
    Retrieves and aggregates tools from a list of MCP client instances.

    Args:
        mcp_clients: A list of client objects (e.g., mcp_client, playwright_mcp_client)
                     that sup`port the 'list_tools()' asynchronous method.
    """

    tools = []

    for client in mcp_client_list:
        client_tools = await client.list_tools()
        tools.extend(client_tools)

    print("Total Tools:", len(tools))

    tool_specs = translate_mcp_tool_to_llm_tool_spec(tools)
    return tool_specs


def translate_mcp_tool_to_llm_tool_spec(tool_list: list[Tool]) -> list:
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


# async def get_tools():
#     async with mcp_client, playwright_mcp_client:
#         tools = await mcp_client.list_tools()
#         tools = []
#         tools.extend(await playwright_mcp_client.list_tools())
#         print("Tools:", len(tools))
#         # print("Tools:", tools)
#         tool_specs = convert_fastapi_to_openai_tools(tools)
#         # print("Converted Tool Specs:", tool_specs)
#         return tool_specs



def main():
    print("Sec: {0}".format(get_secret('AzureOpenAiApiKey')))
    print("Sec: {0}".format(get_secret('Xxx')))

if __name__ == "__main__":
    main()