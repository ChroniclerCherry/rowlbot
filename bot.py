import os
import discord
from dotenv import load_dotenv
import random
from discord.ext import commands

load_dotenv()
bot = commands.Bot(command_prefix='!')
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if random.random() < 0.00001:
        await message.channel.send("AAAAAAAAAAAAAAAAAAAAA")

@bot.command()
async def command(ctx, action, command_name, postID):
    if (action == "add"):
        query = "SELECT * FROM commands"
        with Database as db:
            result = db(query)
            result.fetchall()
    elif(action == "remove"):
        query = "SELECT * FROM commands"

client.run(TOKEN)