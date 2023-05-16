from datetime import datetime
from decouple import config
import discord
import json
import boto3


def save_messages(messages, fname):
    BASE_DIR = "/tmp"
    fname = BASE_DIR + f"/{fname}"
    with open(
        fname,
        mode="w",
    ) as f:
        for message in messages:
            f.write("*" * 64)
            f.write("\n")
            f.write(f"{message['role'].capitalize()}:\n\n")
            f.write(f"{message['content']}\n\n")

    return fname


async def create_private_channel(guild, channel_name, user):
    ## create a private channel

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        user: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_channels=True
        ),
    }
    channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

    return channel


def _get_table():
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = config("AWS_DEFAULT_REGION")
    DYNAMODB_TABLE_NAME = config("DYNAMODB_TABLE_NAME")

    # get dynamodb
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )

    # return table
    return dynamodb.Table(DYNAMODB_TABLE_NAME)


def save_messages_to_db(conversation_id, messages, user_id):
    table = _get_table()
    # put item
    response = table.put_item(
        Item={
            "uuid": conversation_id,
            "user": user_id,
            "messages": json.dumps(messages),
        }
    )

    return response


def load_messages_from_db(conversation_id, user):
    table = _get_table()

    response = table.get_item(Key={"uuid": conversation_id, "user": user})

    return json.loads(response["Item"]["messages"])


def get_conversation_id(channel):
    return "-".join(channel.name.split("-")[:-1])


async def save_conversation(client, channel_id):
    channel = await client.fetch_channel(channel_id)
    conversation_id = get_conversation_id(channel)

    # find the id of the user who had the converstaion with the bot
    # by going through the last 10 messages, aggregate the ids and get rid of the bot id
    conversation_user = [
        msg.author.id
        async for msg in channel.history(limit=10)
        if msg.author.id != 1106096307933814817
    ]  # 1106096307933814817 is the bot id.

    messages = load_messages_from_db(conversation_id, str(conversation_user[0]))

    user_name = await client.fetch_user(f"{conversation_user[0]}")
    created_at = datetime.strftime(channel.created_at, "%Y%m%d")

    fname = f"{user_name.name}-{created_at}-{conversation_id}.txt"
    saved_fname = save_messages(messages, fname)

    conv_dump_channel = await client.fetch_channel(1107963834012008488)

    await conv_dump_channel.send(file=discord.File(saved_fname))
