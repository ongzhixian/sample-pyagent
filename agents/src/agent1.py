import asyncio
import json
from openai import AzureOpenAI
from fastmcp import Client
from mcp_client_utilities import get_tools, tool_to_openai, call_tool_async
from common_utility import get_secret

light_mcp_client = Client('http://localhost:8000/mcp')

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

message_history = [{
    "role": "system",
    "content": "You are a helpful assistant."
}]

# MAIN ASYNC FUNCTION
async def main():
    async with light_mcp_client:
        light_tool_list = await get_tools(light_mcp_client)

        tools_to_client = {}
        for tool in light_tool_list:
            tools_to_client[tool.name] = light_mcp_client
        
        tool_list = light_tool_list
        openai_tools = [tool_to_openai(tool) for tool in tool_list]
        print("Available tools ({0}): ".format(len(tool_list)))
        for tool in tool_list:
            print(f"- {tool.name}: {tool.description}")

        while True:
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input, "User> ")
            if user_input.lower() in ['exit', 'quit']:
                break

            message_history.append({
                "role": "user",
                "content": user_input
            })
            response = client.chat.completions.create(
                model=deployment,
                messages=message_history,
                tools=openai_tools
            )

            selected_response_message = response.choices[0].message

            if selected_response_message.content is not None:
                print(f"Assistant> {selected_response_message.content}")
                message_history.append({
                    "role": selected_response_message.role,
                    "content": selected_response_message.content
                })

            if selected_response_message.tool_calls is not None:
                message_history.append({
                    "role": "assistant",
                    "content": selected_response_message.content,
                    "tool_calls": selected_response_message.tool_calls
                })

                tool_results = []
                for tool_call in selected_response_message.tool_calls:
                    result = await call_tool_async(
                        tools_to_client[tool_call.function.name],
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )

                    message_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": str(result)
                    })

                followup_response = client.chat.completions.create(
                    model=deployment,
                    messages=message_history,
                    tools=openai_tools
                )

                followup_response = followup_response.choices[0].message
                if followup_response.content is not None:
                    print(f"Assistant> {followup_response.content}")
                    message_history.append({
                        "role": "assistant",
                        "content": followup_response.content
                    })


if __name__ == "__main__":
    asyncio.run(main())