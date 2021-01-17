import os
import discord
from dotenv import load_dotenv
import random
import json
from discord.ext import commands
from datetime import datetime
import pytz

##########################################
#             constants                  #
##########################################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_PREFIX = '!'
PREFIXES_PATH = "Data/prefixes.json"
STICKIES_PATH = "Data/stickies.json"


##########################################
#             prefixes                   #
##########################################

def get_prefix(client,message):
    with open(PREFIXES_PATH,'r') as f:
        prefixes = json.load(f)
    
    return prefixes.get(str(message.guild.id), DEFAULT_PREFIX)

def set_prefix(guild_id,prefix):
    with open(PREFIXES_PATH,'r') as f:
        prefixes = json.load(f)
    prefixes[guild_id] = prefix

client = commands.Bot(command_prefix=get_prefix)

@client.event
async def on_guild_join(guild):
    set_prefix(guild.id,DEFAULT_PREFIX)

@client.event
async def on_guild_remove(guild):
    with open(PREFIXES_PATH, "r") as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))
    with open(PREFIXES_PATH, "w") as f:
        json.dump(prefixes, f, indent=4)

@client.command()
async def setprefix(ctx, prefix):
    with open(PREFIXES_PATH, "r") as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    with open(PREFIXES_PATH, "w") as f:
        json.dump(prefixes, f, indent=4)
    await ctx.send(f"Prefix changed to: {prefix}")

##########################################
#             STICKIES                   #
##########################################


@client.command()
async def addsticky(ctx, sticky_name, postID):

    message = await ctx.channel.fetch_message(postID)
    sticky = {
                "message":message.content,
                "author":ctx.author.id,
                "time":pytz.utc.localize(datetime.utcnow()).strftime("%b %d %Y %H:%M:%S") + " UTC",
                "post_id":postID
                }

    with open(STICKIES_PATH,"r") as f:
        stickies = json.load(f)
    
    guid = ctx.guild.id
    
    stickies[guid][sticky_name] = sticky
    with open(STICKIES_PATH, "w") as f:
        json.dump(stickies, f, indent=4, default=str)

    await ctx.channel.send(f"added sticky \"{sticky_name}\"")

@client.command()
async def removesticky(ctx, sticky_name):
    with open(STICKIES_PATH,"r") as f:
        stickies = json.load(f)
    
    guid = str(ctx.guild.id)
    if (guid not in stickies or sticky_name not in stickies[guid])
        await ctx.channel.send(f"There is no sticky named \"{sticky_name}\"")
        return
    
    stickies[guid].pop[sticky_name]
    with open(STICKIES_PATH, "w") as f:
    json.dump(stickies, f, indent=4, default=str)
    await ctx.channel.send(f"Removed sticky \"{sticky_name}\"")

async def post_sticky(message, sticky_name):
    with open(STICKIES_PATH,"r") as f:
            stickies = json.load(f)
    guild_id = str(message.guild.id)

    if (guild_id in stickies and sticky_name in stickies[guild_id]):
        sticky = stickies[guild_id][sticky_name]
        msg = await build_message(message,sticky)
        await message.channel.send(embed = msg)

async def build_message(message,sticky):
    user = await message.guild.fetch_member(sticky["author"])
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name=sticky["message"], value=f"{user.name}#{user.discriminator} " + sticky["time"], inline=False)
    return embedVar
    

##########################################
#             GENERAL                    #
##########################################
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (message.content.startswith(get_prefix(None,message))):
        await post_sticky(message,message.content[1:])

    if random.random() < 0.00001:
        await message.channel.send("AAAAAAAAAAAAAAAAAAAAA")

    await client.process_commands(message)

client.run(TOKEN)