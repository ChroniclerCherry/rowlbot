import os
import discord
from dotenv import load_dotenv
import random
import json
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


def get_prefix(client,message):
    with open("Data/prefixes.json",'r') as file:
        prefixes = json.load(file)
    return prefixes[message.guild.id]

client = commands.Bot(command_prefix = get_prefix)

@client.event
async def on_guild_join(guild):
    with open("Data/prefixes.json",'r') as file:
        prefixes = json.load(file)
    prefixes[guild.id] = '!'

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if random.random() < 0.00001:
        await message.channel.send("AAAAAAAAAAAAAAAAAAAAA")

@client.command()
async def command(ctx, action, command_name, postID):
    print(f"{action} {command_name} {postID}")

client.run(TOKEN)