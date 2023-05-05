# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import os
from decouple import config
from typing import Dict, List


openai.api_key = config("OPENAI_API_KEY")


def get_initial_message(initial_prompt) -> List[Dict]:
    return [{"role": "system", "content": initial_prompt}]


def create_messages(role: str, messages: str) -> Dict:
    return {"role": role, "content": messages}


def get_ai_response(messages: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response