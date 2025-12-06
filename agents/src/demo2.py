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