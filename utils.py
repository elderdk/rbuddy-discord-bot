from datetime import datetime
from decouple import config
import discord
import json
import boto3


def save_messages(messages):
    with open(
        f"{int(datetime.today().timestamp())}_{message.author.id}_conversation.txt",
        mode="w",
    ) as f:
        for message in messages[1:]:
            f.write(f">> {message['role'.capitalize()]}: {message['content']}\n\n")


async def create_private_channel(client, channel_name):
    for g in client.guilds:
        if g.name == config("GUILD_NAME"):
            guild = g

    ## create a private channel

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
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


def save_messages_to_db(client, conversation_id, messages):
    table = _get_table()
    # put item
    response = table.put_item(
        Item={"uuid": conversation_id, "messages": json.dumps(messages)}
    )

    return response


def load_messages_from_db(conversation_id):
    table = _get_table()

    response = table.get_item(
        Key={
            "uuid": conversation_id,
        }
    )

    return json.loads(response["Item"]["messages"])
