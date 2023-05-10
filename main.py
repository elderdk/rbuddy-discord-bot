import discord

# from discord_components import DiscordComponents, Button
from decouple import config
from message_templates import welcome_message, first_ai_prompt, ai_loading_message
from datetime import datetime
from openai_handler import get_initial_message, create_messages, get_ai_response
from utils import (
    create_private_channel,
    save_messages_to_db,
    load_messages_from_db,
)
import requests
from uuid import uuid4


intents = discord.Intents.default()
# intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "!write_welcome":
        channel = await client.fetch_channel(1105669596498903120)
        await channel.send(welcome_message)

    if message.content == "!start":
        # create a private channel and invite the user there, and itself
        ## get the guild
        conversation_id = str(uuid4())
        user = str(message.author.id)
        channel = await create_private_channel(
            client, f"{conversation_id}-learning", message
        )

        await channel.send(content=f"Hi, <@{message.author.id}>, {first_ai_prompt}")

        # delete !start message
        await message.delete()

        ## get the initial prompt
        prompt_storage = client.get_channel(config("PROMPT_STORAGE_CHANNEL", cast=int))

        async for prompt in prompt_storage.history(limit=1):
            initial_prompt = requests.get(prompt.attachments[0].url).text

        messages = get_initial_message(initial_prompt)

        ## save the message history
        response = save_messages_to_db(client, conversation_id, messages, user)

    if message.channel.name.endswith("-learning") and message.author != client.user:
        # send recognition of user message acceptance and display loading
        ai_response = await message.channel.send(ai_loading_message)

        # get the conversation id
        conversation_id = "-".join(message.channel.name.split("-")[:-1])
        user = str(message.author.id)

        # load the messages from db
        messages = load_messages_from_db(conversation_id, user)

        # append the user message
        messages.append(create_messages("user", message.content))

        # Call openai api and get AI reponse
        extracted_ai_msg = get_ai_response(messages)["choices"][0]["message"]["content"]

        # send the AI's response to the user
        await ai_response.edit(content=extracted_ai_msg)

        # save the messages to db
        messages.append(create_messages("assistant", extracted_ai_msg))
        save_messages_to_db(client, conversation_id, messages, user)


client.run(config("BOT_TOKEN"))
