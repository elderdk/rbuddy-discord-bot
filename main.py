import discord

# from discord_components import DiscordComponents, Button
from decouple import config
from commands import process_user_message
from message_templates import welcome_message
from buttons import ViewWithButton
from utils import save_conversation


intents = discord.Intents.default()
# intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)


async def write_welcome_message(client):
    channel = await client.fetch_channel(config("WELCOME_PAGE_ID"))

    # delete all previous messages in the channel
    await channel.purge(limit=1000)

    # load the new welcome page
    await channel.send(welcome_message, view=ViewWithButton(timeout=None))


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await write_welcome_message(client)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    con = message.content

    if con == "!write_welcome":
        await write_welcome_message(client)

    if con.startswith("!save"):
        if con == "!save_all":
            learning_channels = [
                learning_chanel
                for learning_chanel in await message.guild.fetch_channels()
                if learning_chanel.name.endswith("-learning")
            ]
            for channel in learning_channels:
                await save_conversation(client, channel.id)
        else:
            channel_id = con.split(" ")[1]  # e.g. !save 123123123123123
            await save_conversation(
                client, channel_id
            )  # iterate all channels and save them one-by-one

    if message.channel.name.endswith("-learning") and message.author != client.user:
        await process_user_message(message)


client.run(config("BOT_TOKEN"))
