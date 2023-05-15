# Code below is for AWS Lambda-based automatic channel deleter function
# Copy/paste this to a lambda function and set Eventbridge as its trigger


import json
import os
from datetime import datetime, timezone
import discord


intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def delete_expired_channels(client):
    # get a list of channels with '-learning' suffix
    channels = [
        channel
        for channel in client.get_all_channels()
        if channel.name.endswith("-learning")
    ]

    # iterate the channels, check the elapsed time, delete if day >= 1
    for channel in channels:
        now = datetime.now().replace(tzinfo=timezone.utc)
        delta = now - channel.created_at
        if delta.days >= os.environ["DELETE_N_DAYS_LATER"]:
            print(f"deleting {channel.name}: delta.days = {delta.days}")
            await channel.delete()


@client.event
async def on_ready():
    # turn on the bot
    await delete_expired_channels(client)

    # terminate the bot
    await client.close()


def lambda_handler(event, context):
    client.run(os.environ["BOT_TOKEN"])
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
