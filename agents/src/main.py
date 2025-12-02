from ollama import chat
from ollama import ChatResponse

chat_history = []

if __name__ == "__main__":
    chat_history.append({
        'role': 'user',
        'content': 'Hello, how are you?',
    })

    response: ChatResponse = chat(model='phi4-mini:latest', messages=chat_history)

    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)
