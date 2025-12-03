from openai import AzureOpenAI
from openai.types.chat import chat_completion_message
from common_utility import get_secret

endpoint = "https://eastus.api.cognitive.microsoft.com/"
model_name = "gpt-5-nano"
deployment = "gpt-5-nano"
# model_name = "o4-mini"
# deployment = "o4-mini"

subscription_key = get_secret('AzureOpenAiApiKey')
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

message_history = [{
    "role": "system",
    "content": "You are a helpful assistant.",
}]


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
        model=deployment
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
