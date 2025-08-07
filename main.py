import discord
from discord import app_commands
from decouple import config
import json

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
TOKEN = config("TOKEN")

