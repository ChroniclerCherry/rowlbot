import os
import discord
from dotenv import load_dotenv
import random
import json
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests

from datetime import datetime
import pytz
import re

##########################################
#             constants                  #
##########################################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_PREFIX = '!'
PREFIXES_PATH = "Data/prefixes.json"
STICKIES_PATH = "Data/stickies.json"
IDs_PATH = "Data/FRIDs.json"

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

client = commands.Bot(
    command_prefix=get_prefix,
    description='i screm',
    case_insensitive=True
)

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

@client.command(
    help=f"prefix - new prefix for commands",
	brief="Change the prefix for commands for this bot.")
async def prefix(ctx, subcommand = None, prefix = None):
    if (subcommand == "set"):
        set_prefix_command(ctx,prefix)
    elif (subcommand == None):
        prefix = get_prefix(ctx,ctx.message)
        msg = discord.Embed(title="Prefix Help",color=0x63C383, description = f"The current prefix for this bot is `{prefix}`")
        msg.add_field(name=f"{prefix}prefix set <prefix>", value=f"Changes the current prefix used by the bot on this server to the given prefix", inline=False)
        await ctx.channel.send(embed = msg)


async def set_prefix_command(ctx,prefix):
    with open(PREFIXES_PATH, "r") as f:
        prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = prefix

    with open(PREFIXES_PATH, "w") as f:
        json.dump(prefixes, f, indent=4)
    
    await ctx.send(f"Prefix changed to: {prefix}")
##########################################
#             STICKIES                   #
##########################################

STICKY_MESSAGE = "message"
STICKY_AUTHOR = "author"
STICKY_TIME = "time"
STICKY_MESSAGE_ID = "message_id"
STICKY_JUMP_URL = "jump_url"
STICKY_IMAGE_URL = "image_url"
STICKY_EMBEDED = "embed"
STICKY_TYPE = "type"
STICKY_TYPE_IMAGE = "STICKY_TYPE_IMAGE"
STICKY_TYPE_DEFAULT = "STICKY_TYPE_DEFAULT"

@client.command(
    help=f"",
	brief="Add, Remove, and View stickies in this server")
async def sticky (ctx, subcommand = None, sticky_name = None, message_id = None, embed = True):
    if subcommand == "add":
        await add_sticky(ctx,sticky_name,message_id,embed),
    if subcommand == "add_image":
        await add_image(ctx,sticky_name,message_id),
    elif subcommand == "list":
        await list_stickies(ctx),
    elif subcommand == "remove":
        await remove_sticky(ctx,sticky_name)
    elif subcommand == None:
        prefix = get_prefix(ctx,ctx.message)
        msg = discord.Embed(title="Stickies Help",color=0x63C383, description = f"Stickies let you save posts to a command to easily bring up later with `{prefix}<sticky name>`")
        msg.add_field(name=f"{prefix}sticky add <sticky_name> <message_id> <embed>", value=f"Adds the given message at message_id to the command sticky_name.\nUsing the same sticky_name as an existing sticky will override it.\nEmbeded is optional and defaults to true", inline=False)
        msg.add_field(name=f"{prefix}sticky add_image <sticky_name> <image_url>", value=f"Adds a single image as a sticky", inline=False)
        msg.add_field(name=f"{prefix}sticky list", value=f"Lists all current stickies", inline=False)
        msg.add_field(name=f"{prefix}sticky remove <sticky_name>", value=f"Removes the sticky at the given name", inline=False)
        await ctx.channel.send(embed = msg)

async def add_image(ctx,sticky_name,image_url):
    sticky = {
        STICKY_AUTHOR:ctx.author.id,
        STICKY_TIME:pytz.utc.localize(datetime.utcnow()).strftime("%b %d %Y %H:%M:%S") + " UTC",
        STICKY_IMAGE_URL:image_url,
        STICKY_TYPE:STICKY_TYPE_IMAGE }

    with open(STICKIES_PATH,"r") as f:
        stickies = json.load(f)
    
    guid = str(ctx.guild.id)
    if (guid not in stickies):
        stickies[guid] = {}
    
    stickies[guid][sticky_name] = sticky
    with open(STICKIES_PATH, "w") as f:
        json.dump(stickies, f, indent=4, default=str)

    await ctx.channel.send(f"added sticky \"{sticky_name}\"")

async def add_sticky(ctx, sticky_name, postID, embed = True):
    message = await ctx.channel.fetch_message(postID)
    sticky = {
                STICKY_MESSAGE:message.content,
                STICKY_AUTHOR:message.author.id,
                STICKY_TIME:pytz.utc.localize(datetime.utcnow()).strftime("%b %d %Y %H:%M:%S") + " UTC",
                STICKY_MESSAGE_ID:postID,
                STICKY_JUMP_URL:message.jump_url,
                STICKY_EMBEDED:embed,
                STICKY_TYPE : STICKY_TYPE_DEFAULT
                }

    with open(STICKIES_PATH,"r") as f:
        stickies = json.load(f)
    
    guid = str(ctx.guild.id)
    if (guid not in stickies):
        stickies[guid] = {}
    
    stickies[guid][sticky_name] = sticky
    with open(STICKIES_PATH, "w") as f:
        json.dump(stickies, f, indent=4, default=str)

    await ctx.channel.send(f"added sticky \"{sticky_name}\"")

async def remove_sticky(ctx, sticky_name):
    with open(STICKIES_PATH,"r") as f:
        stickies = json.load(f)
    
    guid = str(ctx.guild.id)
    if (guid not in stickies or sticky_name not in stickies[guid]):
        await ctx.channel.send(f"There is no sticky named \"{sticky_name}\"")
        return
    
    stickies[guid].pop(sticky_name)
    with open(STICKIES_PATH, "w") as f:
        json.dump(stickies, f, indent=4, default=str)
    await ctx.channel.send(f"Removed sticky \"{sticky_name}\"")

async def list_stickies(ctx):
    response = discord.Embed(color=0x63C383)
    guid = str(ctx.guild.id)
    prefix = get_prefix(ctx,ctx.message)
    with open(STICKIES_PATH,"r") as f:
        stickies = json.load(f)
    
    stickies_list = ""
    if (guid in stickies):
        for key in stickies[guid]:
            stickies_list += f"{prefix}{key}\n"
    else:
        stickies_list = "No stickies yet"
    response.add_field(name=f"Stickies in {ctx.guild.name}",value=stickies_list,inline=False)
    await ctx.channel.send(embed=response)

async def post_sticky(message, sticky_name):
    with open(STICKIES_PATH,"r") as f:
            stickies = json.load(f)
    guild_id = str(message.guild.id)

    if (guild_id in stickies and sticky_name in stickies[guild_id]):
        sticky = stickies[guild_id][sticky_name]
        user = await message.guild.fetch_member(sticky["author"])

        if (sticky[STICKY_TYPE] == STICKY_TYPE_IMAGE):
            msg = discord.Embed()
            msg.set_image(url=sticky[STICKY_IMAGE_URL])
            await message.channel.send(embed = msg)
        elif sticky[STICKY_EMBEDED] == False:
            msg = sticky["message"]
            await message.channel.send(msg)
        else:
            msg = discord.Embed(color=0x63C383,description=sticky["message"])
            msg.add_field(name=f"\t- {user.name}#{user.discriminator} "+sticky["time"], value=f"[Click to go to post]({sticky[STICKY_JUMP_URL]})")
            await message.channel.send(embed = msg)

##########################################
#                 D&D                    #
##########################################

@client.command(
    help=f"dice - standard d&d dice format, i.e. 2d20+1",
	brief="Roll dice")
async def roll(ctx, dice):
    block = discord.Embed(color=0x63C383)
    d_index = int(dice.find('d'))
    plus_index = int(dice.find('+'))
    if (d_index == 0):
        num_dice = 1
    else:
        num_dice = int(dice[:d_index])
    if (plus_index == -1):
        modifier = 0
        dice_type = int(dice[d_index+1:])
    else:
        dice_type = int(dice[d_index+1:plus_index])
        modifier = int(dice[plus_index+1:])

    total = modifier
    roll = f"("
    for n in range(num_dice):
        rng = random.randint(1,dice_type)
        total += rng
        roll += str(rng) + " "

    roll += f")\nTotal: {total}"
    block.add_field(name=f"Rolling {dice}", value=roll, inline=False)
    await ctx.channel.send(embed = block)


##########################################
#           FLIGHT RISING                #
##########################################

publish_interval_minutes = 10
minutes_since_last_publish = 10

@client.command(help=f"track = true or false, to post current IDs in this channel")
async def FR_IDs(ctx, track):
    if (track == "now"):
        id_info = GetCurrentID()
        await ctx.channel.send(id_info)
    else:
        with open(IDs_PATH,'r') as f:
            IDs_data = json.load(f)

        if (track == "true"):
            if (ctx.channel.id not in IDs_data["channels"]):
                IDs_data["channels"].append(ctx.channel.id)
                await ctx.send(f"Flight rising ID tracking enabled for this channel")
        elif (track == "false"):
            if (ctx.channel.id in IDs_data["channels"]):
                IDs_data["channels"].remove(ctx.channel.id)
                await ctx.send(f"Flight rising ID tracking disabled for this channel")
        else:
            try:
                global publish_interval_minutes
                publish_interval_minutes = int(track)
                await ctx.send(f"Time interval set to : {track}")
            except ValueError:
                await ctx.send(f"Unknown command.")
            

        with open(IDs_PATH, "w") as f:
            json.dump(IDs_data, f, indent=4)

@tasks.loop(minutes=1)
async def check_ids_task():
    global minutes_since_last_publish
    global publish_interval_minutes

    if (minutes_since_last_publish == publish_interval_minutes):
        minutes_since_last_publish = 1
    else:
        minutes_since_last_publish += 1
        return

    id_info = GetCurrentID()
    with open(IDs_PATH,'r') as f:
        IDs_data = json.load(f)

    for channel_id in IDs_data["channels"]:
        channel = client.get_channel(id=channel_id)
        await channel.send(id_info)


def GetCurrentID():
    load_dotenv()
    COOKIE = os.getenv('FLIGHT_RISING_COOKIE')
    url = 'https://www1.flightrising.com/search/dragons?page=1&sort=id_asc&name=&exalted=0&progen=&breed=&bodygene=&winggene=&tertgene=&gender=&body=&wings=&tert=&element=&body_range=&wings_range=&tert_range=&age=&rtb=&gen1=&pattern=&id_length=&level_min=&level_max=&eyetype=&hibernal_cooldown_status=&ancient=&named=&hibernal=&silhouette_unlocked=&sort=id_desc&page=1'
    headers = {'User-Agent': 'Mozilla/5.0','Cookie':COOKIE}

    try:
        r = requests.get(url,headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        id_block = soup.find("div",{"class":"dragon-search-result-level"}).contents[0]
        id = re.search('([^\s]+)', id_block).group(0)

        time = soup.find("span",{"class":"time common-tooltip"})['title']
        return "Current ID: " + id + " | FR Time: " + time + " | Current Time: " + pytz.utc.localize(datetime.utcnow()).strftime("%b %d %Y %H:%M:%S") + " UTC"
    except AttributeError:
        return "Login Cookie expired, please bother Chronicler#9318 to renew it"

##########################################
#             GENERAL                    #
##########################################
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    check_ids_task.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(f'<@{client.user.id}>') or message.content.startswith(f'<@!{client.user.id}>'):
        message.content = message.content.replace(f'<@{client.user.id}> ',get_prefix(None,message))
        message.content = message.content.replace(f'<@!{client.user.id}> ',get_prefix(None,message))
        await client.process_commands(message)
        return

    if (message.content.startswith(get_prefix(None,message))):
        await post_sticky(message,message.content[1:])

    if (message.author.id != 287009371966406667 and random.random() < 0.05 and message.guild.id == 673715193984974904) and "animat" in message.content.lower():
        await message.channel.send("_Summons gervig_")

    if random.random() < 0.001:
        await message.channel.send("AAAAAAAAAAAAAAAAAAAAA")

    await client.process_commands(message)

client.run(TOKEN)