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
# model_name = "gpt-5-nano"
# deployment = "gpt-5-nano"


subscription_key = get_secret('AzureOpenAiApiKey')
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

async def llm_chat():
    async with mcp_client:
        tool_specs = await get_tools(mcp_client)
        
        message_history = [{
            "role": "system",
            "content": "You are a helpful assistant.",
        }]

        user_input = ""

        # print("Enable multiple tool calls per response? (y/n): ", end="")
        # multi_tool_mode = input().strip().lower() == "y"
        # print("Print tool results to user? (y/n): ", end="")
        # print_tool_result = input().strip().lower() == "y"
        multi_tool_mode = False
        print_tool_result = True

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
                tools=tool_specs,
            )

            if len(response.choices) > 0:
                if len(response.choices) > 1:
                    print("Warning: Multiple responses received, only the first will be processed.")
                chosen_response = response.choices[0]
                # print(chosen_response)
                if isinstance(chosen_response.message, chat_completion_message.ChatCompletionMessage):
                    chosen_response_message = chosen_response.message
                    # Ensure assistant content is a non-null string
                    assistant_content = chosen_response_message.content if chosen_response_message.content is not None else ""
                    print(assistant_content)
                    message_history.append({
                        "role": "assistant",
                        "content": assistant_content,
                    })

                    # Tool call support
                    tool_calls = getattr(chosen_response_message, "tool_calls", None)
                    if tool_calls:
                        if not multi_tool_mode:
                            tool_calls = [tool_calls[0]]
                        import json
                        for tool_call in tool_calls:
                            tool_name = tool_call.function.name
                            tool_args_raw = tool_call.function.arguments
                            try:
                                # Parse arguments from JSON string to dict
                                if isinstance(tool_args_raw, str):
                                    tool_args = json.loads(tool_args_raw)
                                else:
                                    tool_args = tool_args_raw
                                tool_result = await mcp_client.call_tool(tool_name, tool_args)
                                if print_tool_result:
                                    print(f"Tool '{tool_name}' result: {tool_result}")
                                # OpenAI expects 'tool_call_id' and string 'content' for tool messages
                                tool_call_id = getattr(tool_call, "id", None)
                                # Ensure tool content is a non-null string
                                tool_content = str(tool_result) if tool_result is not None else ""
                                message_history.append({
                                    "role": "tool",
                                    "content": tool_content,
                                    "tool_call_id": tool_call_id if tool_call_id else "tool_call_id_missing",
                                })
                            except Exception as e:
                                print(f"Error calling tool '{tool_name}': {e}")
                        # After tool calls, send follow-up to LLM to answer initial query
                        followup_response = client.chat.completions.create(
                            messages=message_history,
                            max_completion_tokens=13107,
                            temperature=1.0,
                            top_p=1.0,
                            frequency_penalty=0.0,
                            presence_penalty=0.0,
                            model=deployment,
                            tools=tool_specs,
                        )
                        if len(followup_response.choices) > 0:
                            followup_message = followup_response.choices[0].message
                            followup_content = followup_message.content if followup_message.content is not None else ""
                            print(f"Assistant: {followup_content}")
                            message_history.append({
                                "role": "assistant",
                                "content": followup_content,
                            })
                    # Only send 'tool' messages and follow-up requests if tool_calls is present
                else:
                    print(f"Error: Unexpected message format in response. {chosen_response}")


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