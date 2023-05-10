# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import os
from decouple import config
from typing import Dict, List
from message_templates import first_ai_prompt


openai.api_type = "azure"
openai.api_base = "https://riiid-openai-playground.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = config("OPENAI_API_KEY")


def get_initial_message(initial_prompt) -> List[Dict]:
    return [
        {"role": "system", "content": initial_prompt},
        {"role": "user", "content": "Hi."},
        {"role": "assistant", "content": f"Hi! {first_ai_prompt}"},
    ]


def create_messages(role: str, messages: str) -> Dict:
    return {"role": role, "content": messages}


def get_ai_response(messages: str):
    response = openai.ChatCompletion.create(
        engine="openai-gpt-4",
        messages=messages,
    )
    return response
