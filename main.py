import discord
from discord import app_commands
import decouple
import json
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
TOKEN = decouple.config("TOKEN")

def LoadJson(path: str) -> dict:
    if os.path.exists(f"{os.getcwd()}\\{path}"):
        with open(f"{os.getcwd()}\\{path}", "r", encoding="utf8") as f:
            return json.load(f)
    else:
        with open(f"{os.getcwd()}\\{path}", "x+") as f:
            json.dump({}, f, indent=4)
            return {}
        
def DumpJson(path: str, dict: dict) -> None:
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
    @app_commands.describe(bracket="What you want the bracket to be")
    @app_commands.checks.has_permissions(administrator=True)
    async def setbracket(self, interaction: discord.Interaction, bracket: str):
        configs[str(interaction.guild.id)]["brackets"] = bracket
        DumpJson("configs.json", configs)

        await interaction.response.send_message(f"Brackets have been set to `{bracket}`")

    @app_commands.command(name="add", description="Adds the given preset with given name to presets.")
    @app_commands.describe(name="The name for the preset that will be used between brackets", preset="The replacement text/string the name in brackets will be replaced with")
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction: discord.Interaction, name: str, preset: str):
        if name.lower() not in  presets[str(interaction.guild.id)].keys():
            presets[str(interaction.guild.id)][name.lower()] = preset

            DumpJson("presets.json", presets)

            brackets = configs[str(interaction.guild.id)]["brackets"]
            await interaction.response.send_message(f"Added a preset, {brackets}{name.lower()}{brackets} will now be replaced by {preset}")

        else:
            await interaction.response.send_message(f"ERROR: This preset already exists. Please use /preset edit to edit the preset, instead.")

    @app_commands.command(name="edit", description="Edits the preset with given name.")
    @app_commands.describe(name="The name of the preset that you want to edit", preset="The new replacement text/string the name in brackets will be replaced with", new_name="The new name for the preset")
    @app_commands.checks.has_permissions(administrator=True)
    async def edit(self, interaction: discord.Interaction, name: str, preset: str = None, new_name: str = None):
        newName = new_name

        if name.lower() in presets[str(interaction.guild.id)].keys():
            if preset != None:
                presets[str(interaction.guild.id)][name.lower()] = preset 

            if newName != None:
                presets[str(interaction.guild.id)][newName.lower()] = presets[str(interaction.guild.id)].pop(name.lower())

            DumpJson("presets.json", presets)

            brackets = configs[str(interaction.guild.id)]["brackets"]

            if preset != None and newName != None:
                await interaction.response.send_message(f"Edited the preset {name.lower()}. {brackets}{newName.lower()}{brackets} will now be replaced by {preset}")
            elif preset == None and newName != None:
                await interaction.response.send_message(f"Edited the preset {name.lower()}. {brackets}{newName.lower()}{brackets} will now be replaced by {presets[str(interaction.guild.id)][newName.lower()]}")
            elif preset != None and newName == None:
                await interaction.response.send_message(f"Edited the preset {name.lower()}. {brackets}{name.lower()}{brackets} will now be replaced by {preset}")
            else:
                await interaction.response.send_message("ERROR: No edits were given, please use one or both of the optional paramaters (`preset` or `new_name`)")
        else:
            await interaction.response.send_message("ERROR: This preset doesn't exist. Please use /preset add to add a new preset, instead.")
    
    class removeConfirmation(discord.ui.View):
        def __init__(self, user: discord.User, name: str):
            super().__init__(timeout=60)
            self.user = user
            self.name = name

        @discord.ui.button(label="Confirm removal of preset", style=discord.ButtonStyle.danger, emoji="✖")
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            presets[str(interaction.guild.id)].pop(self.name.lower())
            DumpJson("presets.json", presets)
            await interaction.response.edit_message(content=f"Preset {self.name.lower()} was removed", view=None)

        async def interaction_check(self, interaction):
            if interaction.user != self.user:
                interaction.response.send_message("ERROR: Only the creator of this button is allowed to interact with it", ephemeral=True)
                return False
            elif interaction.user == self.user:
                return True


    @app_commands.command(name="remove", description="Removes the preset with given name.")
    @app_commands.describe(name="The name of the preset that you want to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, name: str):

        if name.lower() in presets[str(interaction.guild.id)].keys():
            view = preset.removeConfirmation(user=interaction.user, name=name)
            await interaction.response.send_message("Are you sure you want to remove this preset?", view=view)

        else:
            await interaction.response.send_message("ERROR: This preset doesn't exist.")

    
    
tree.add_command(preset())

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(TOKEN)