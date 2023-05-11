import discord
from commands import start_convo


class ViewWithButton(discord.ui.View):
    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Hey R.buddy👋🏽")
    async def button_one(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await start_convo(button)

    @discord.ui.button(
        style=discord.ButtonStyle.blurple, label="Learn more about R.buddy"
    )
    async def button_two(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        print("Button2 clicked")
