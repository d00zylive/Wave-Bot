import discord
from discord import app_commands
from decouple import config
import json
import os

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
TOKEN = config("TOKEN")

def LoadJson(path: str):
    if os.path.exists(f"{os.getcwd()}\\{path}"):
        with open(f"{os.getcwd()}\\{path}", "r", encoding="utf8") as f:
            return json.load(f)
    else:
        with open(f"{os.getcwd()}\\{path}", "x+") as f:
            json.dump({}, f, indent=4)
            return {}

presets = LoadJson("presets.json")
configs = LoadJson("configs.json")

class preset(app_commands.Group):
    def __init__(self):
        super().__init__(name="preset", description="Commands related to presets")

    @app_commands.command(name="generate", description="Replaces the name of a preset surrounded in brackets with the preset correlated to said name")
    @app_commands.describe(text="The text you want to add presets into")
    async def generate(self, interaction: discord.Interaction, text: str) -> str:
        localPresets: dict = presets[str(interaction.guild.id)]
        localConfigs: dict = configs[str(interaction.guild.id)]
        response = ""
        for substr in text.split(sep=localConfigs["brackets"]):
            if substr.lower() in localPresets.keys():
                substr = localPresets[substr.lower()]
            response += substr
        await interaction.response.send_message(response)

tree.add_command(preset())

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(TOKEN)