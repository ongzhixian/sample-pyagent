import asyncio
from openai import AzureOpenAI
from openai.types.chat import chat_completion_message
from fastmcp import Client
from mcp.types import Tool
from common_utility import get_secret, get_tools

mcp_client = Client("http://localhost:8000/mcp")
playwright_mcp_client = Client('http://localhost:8931/mcp')

endpoint = "https://eastus.api.cognitive.microsoft.com/"
model_name = "gpt-4.1"
deployment = "gpt-4.1"

subscription_key = get_secret('AzureOpenAiApiKey')
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

async def llm_chat():
    message_history = [{
        "role": "system",
        "content": "You are a world-class software engineer.",
    }]

    # async with mcp_client, playwright_mcp_client:
    #     tool_specs = await get_tools(mcp_client, playwright_mcp_client)

    async with mcp_client:
        tool_specs = await get_tools(mcp_client)
        user_input = ""

        while user_input.lower() != "/bye":

            user_input = input("User> ")

            message_history.append({
                "role": "user",
                "content": user_input,
            })

            response = client.chat.completions.create(
                messages=message_history,
                max_completion_tokens=13107,
                temperature=1.0,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                model=deployment,
                tools=tool_specs,  # Pass the tool schema here
            )

            if len(response.choices) > 0:
                if len(response.choices) > 1:
                    print("Warning: Multiple responses received, only the first will be processed.")
                chosen_response = response.choices[0]
                if isinstance(chosen_response.message, chat_completion_message.ChatCompletionMessage):
                    chosen_response_message = chosen_response.message
                    print(chosen_response_message.content)
                    message_history.append({
                        "role": "assistant",
                        "content": chosen_response_message.content,
                    })
                else:
                    print("Error: Unexpected message format in response. {0}".format(chosen_response))


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
    # asyncio.run(run())
    asyncio.run(llm_chat())