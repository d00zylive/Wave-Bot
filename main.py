import discord
from discord import app_commands
from decouple import config
import json
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
TOKEN = config("TOKEN")

def LoadJson(path: str) -> dict:
    if os.path.exists(f"{os.getcwd()}\\{path}"):
        with open(f"{os.getcwd()}\\{path}", "r", encoding="utf8") as f:
            return json.load(f)
    else:
        with open(f"{os.getcwd()}\\{path}", "x+") as f:
            json.dump({}, f, indent=4)
            return {}
        
def DumpJson(path: str, dict: dict):
    with open(f"{os.getcwd()}\\{path}", "w", encoding="utf8") as f:
        json.dump(dict, f, indent=4)

presets = LoadJson("presets.json")
configs = LoadJson("configs.json")

class preset(app_commands.Group):
    def __init__(self):
        super().__init__(name="preset", description="Commands related to presets")

    @app_commands.command(name="generate", description="Replaces the name of a preset surrounded in brackets with the preset correlated to said name")
    @app_commands.describe(text="The text you want to add presets into")
    async def generate(self, interaction: discord.Interaction, text: str):
        localPresets: dict = presets[str(interaction.guild.id)]
        localConfigs: dict = configs[str(interaction.guild.id)]
        response = ""
        for substr in text.split(sep=localConfigs["brackets"]):
            if substr.lower() in localPresets.keys():
                substr = localPresets[substr.lower()]
            response += substr
        await interaction.response.send_message(response)

    @app_commands.command(name="linkgenerate", description="This does the same as /preset generate, except it uses a message link")
    @app_commands.describe(link="The message where you wanna use presets")
    async def linkgenerate(self, interaction: discord.Interaction, link: str):

        guildId, channelId, messageId = link.split(sep="/")[-3:]
        if guildId == str(interaction.guild.id) and int(channelId) in [channel.id for channel in interaction.guild.channels]:
            try:
                channel = await client.fetch_channel(channelId)
                message = await channel.fetch_message(messageId)
                text = message.content
            except discord.errors.NotFound:
                await interaction.response.send_message("ERROR: The message couldn't be found, make sure it still exists", ephemeral=True)
                return
            except discord.errors.Forbidden:
                await interaction.response.send_message("ERROR: This bot does not have the permissions to access this message", ephemeral=True)
                return
        else:
            await interaction.response.send_message("ERROR: The link was invalid, from another server or the bot doesn't have the permissions to access the channel", ephemeral=True)
            return

        localPresets: dict = presets[str(interaction.guild.id)]
        localConfigs: dict = configs[str(interaction.guild.id)]
        response = ""
        for substr in text.split(sep=localConfigs["brackets"]):
            if substr.lower() in localPresets.keys():
                substr = localPresets[substr.lower()]
            response += substr
        await interaction.response.send_message(response)
    
    @app_commands.command(name="setbracket", description="Sets the bracket to the given string. The bracket \"++\" with preset star would look like \"++star++\"")
    @app_commands.describe(bracket="What you want the bracket to do")
    @app_commands.checks.has_permissions(administrator=True)
    async def setbracket(self, interaction: discord.Interaction, bracket: str):
        configs[str(interaction.guild.id)]["brackets"] = bracket
        DumpJson("configs.json", configs)
        await interaction.response.send_message(f"Brackets have been set to `{bracket}`")
tree.add_command(preset())

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(TOKEN)