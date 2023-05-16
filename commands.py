from uuid import uuid4
from utils import (
    create_private_channel,
    save_messages_to_db,
    load_messages_from_db,
    get_conversation_id,
)
from openai_handler import get_initial_message, get_ai_response, create_messages
from message_templates import ai_loading_message
import requests
from decouple import config
from message_templates import first_ai_prompt


async def start_convo(button):
    # create a private channel and invite the user there, and itself
    ## get the guild
    conversation_id = str(uuid4())
    user = str(button.user.id)
    channel = await create_private_channel(
        button.guild, f"{conversation_id}-learning", button.user
    )

    await channel.send(content=f"Hi, <@{button.user.id}>, {first_ai_prompt}")

    ## get the initial prompt
    prompt_storage = button.client.get_channel(
        config("PROMPT_STORAGE_CHANNEL", cast=int)
    )

    async for prompt in prompt_storage.history(limit=1):
        initial_prompt = requests.get(prompt.attachments[0].url).text

    messages = get_initial_message(initial_prompt)

    ## save the message history
    response = save_messages_to_db(conversation_id, messages, user)

    ## suppress interaction failed message
    await button.response.defer()


async def process_user_message(message):
    # send recognition of user message acceptance and display loading
    ai_response = await message.channel.send(ai_loading_message)

    # get the conversation id
    conversation_id = get_conversation_id(message.channel)
    user = str(message.author.id)

    # load the messages from db
    messages = load_messages_from_db(conversation_id, user)

    # append the user message
    messages.append(create_messages("user", message.content))

    # Call openai api and get AI reponse

    try:
        # Get the response
        temp_response = get_ai_response(messages)
        finish_reason = temp_response["choices"][0]["finish_reason"]

        # Flag an error if the finish reason is abnormal, i.e. nt "stop"
        if finish_reason != "stop":
            response = f"Something went wrong... The AI finished with the following reason: `{finish_reason}.` Please flag the admin! Sorry for the inconvenience. We'll try to fix it ASAP!"
        else:
            response = temp_response["choices"][0]["message"]["content"]

    except Exception as e:
        response = f"Sorry! Something went wrong. You can go back to the welcome page and try clicking the \"R Buddy\" button again. If it still doesn't work, please flag the admin! It's probably fine but here's the error message.: {e}"

    # send the AI's response to the user
    await ai_response.edit(content=response)

    # save the messages to db
    messages.append(create_messages("assistant", response))
    save_messages_to_db(conversation_id, messages, user)
