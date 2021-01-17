import os
import discord
from dotenv import load_dotenv
import random
import json
from discord.ext import commands

def get_prefix(client,message):
    with open("Data/prefixes.json",'r') as file:
        prefixes = json.load(file)
    
    if (message.guild.id in prefixes):
        return prefixes[message.guild.id]
    else:
        set_prefix(message.guild.id,DEFAULT_PREFIX)
        return DEFAULT_PREFIX

def set_prefix(guild_id,prefix):
    with open("Data/prefixes.json",'r') as file:
        prefixes = json.load(file)
    prefixes[guild_id] = prefix
    
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_PREFIX = '!'
client = commands.Bot(command_prefix = get_prefix)

@client.event
async def on_guild_join(guild):
    set_prefix(guild.id,DEFAULT_PREFIX)

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
async def sticky(ctx, action, command_name, postID):
    print(f"{action} {command_name} {postID}")

client.run(TOKEN)