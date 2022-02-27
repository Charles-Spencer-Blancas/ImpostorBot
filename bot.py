import json
from json import JSONDecodeError
import dateutil
from discord import HTTPException
from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import random
from pathlib import Path
import datetime
from json import JSONEncoder
import dateutil.parser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# TOKEN = os.environ['TOKEN']
global bot
bot = commands.Bot(command_prefix='$')

global currentMemberCopying
currentMemberCopying = ''
global possibleSayings
possibleSayings = []
global textDatabase
global timeDatabase
global replyOnly
replyOnly = False
global current_impersonate
current_impersonate = 0

# data reload
fle = Path('data.json')
fle.touch(exist_ok=True)
f = open(fle)
with open('data.json') as json_file:
    try:
        data = json.load(json_file)
        # Print the type of data variable
        print("Type:", type(data))
        textDatabase = data
        print("first")
        print(textDatabase)
    except JSONDecodeError:
        print("decode")
        textDatabase = dict()
        print(textDatabase)
fle = Path('time.json')
fle.touch(exist_ok=True)
f = open(fle)
with open('time.json') as json_file_time:
    try:
        time_data = json.load(json_file_time)
        # decode
        for channel in time_data:
            for user in time_data[channel]:
                time_data[channel][user] = dateutil.parser.parse(time_data[channel][user])
        # Print the type of data variable
        print("Type:", type(data))
        timeDatabase = time_data
        print("first_time")
        print(timeDatabase)
    except JSONDecodeError:
        print("decode_time")
        timeDatabase = dict()
        print(timeDatabase)
# initialize possibleSayings
if len(textDatabase) != 0:
    first_key_channel = list(textDatabase.keys())[0]
    possibleSayings_1 = textDatabase[first_key_channel]
    first_key_user = list(possibleSayings_1.keys())[0]
    possibleSayings = possibleSayings_1[first_key_user]
else:
    possibleSayings.append('nothing to say, plz impersonate')

async def reload_possibleSayings(userId, channelId):
    global possibleSayings
    if str(channelId) in textDatabase:
        if str(userId) in textDatabase[str(channelId)]:
            # temporary possibleSayings from offline json
            possibleSayings = textDatabase[str(channelId)][str(userId)]
async def append_possibleSayings(userId, channelId):
    global possibleSayings
    if str(channelId) in textDatabase:
        if str(userId) in textDatabase[str(channelId)]:
            # temporary possibleSayings from offline json
            possibleSayings += textDatabase[str(channelId)][str(userId)]


async def history_helper(ctx, user, userId, channel, channelId, currentMemberCopying, textDatabase, timeDatabase):
    global possibleSayings
    global current_impersonate
    # QUICK CHANGE first, load offline json, TODO quick get name
    currentMemberCopying = ctx.message.mentions[0].display_name
    await ctx.guild.me.edit(nick=currentMemberCopying)
    if current_impersonate != userId:
        await reload_possibleSayings(userId, channelId)

    # fetch messages after if date exist
    h = []
    if str(channelId) in timeDatabase:
        if str(userId) in timeDatabase[str(channelId)]:
            h = await channel.history(limit=9999, after=timeDatabase[str(channelId)][str(userId)]).flatten()
        else:
            h = await channel.history(limit=9999).flatten()
    elif str(channelId) not in timeDatabase:
        h = await channel.history(limit=9999).flatten()

    # check if user has been called before
    filteredMessages = []
    filteredMessages = [message for message in h if message.author.id == userId]

    # check if channel has ever been scraped
    if str(channelId) in timeDatabase:
        if str(userId) in timeDatabase[str(channelId)]:
            print("current time database", timeDatabase[str(channelId)][str(userId)])
            if filteredMessages is not None:
                filteredMessages = [message for message in filteredMessages if
                                    timeDatabase[str(channelId)][str(userId)] < message.created_at]
    else:
        timeDatabase[str(channelId)] = dict()

    # check if there are new messages
    if len(filteredMessages) == 0:
        return
    # update time
    timeDatabase[str(channelId)][str(userId)] = filteredMessages[0].created_at
    # to rename bot

    possibleSayings_temp = [message.content for message in filteredMessages]
    print(str(channelId) in textDatabase)
    # Update texts to database
    if str(channelId) in textDatabase:
        if str(userId) in textDatabase[str(channelId)]:
            # temporary possibleSayings from offline json
            possibleSayings = textDatabase[str(channelId)][str(userId)]
            for text in reversed(possibleSayings_temp):
                textDatabase[str(channelId)][str(userId)].append(text)
        else:
            textDatabase[str(channelId)][str(userId)] = []
            for text in reversed(possibleSayings_temp):
                textDatabase[str(channelId)][str(userId)].append(text)
    else:
        textDatabase[str(channelId)] = dict()
        textDatabase[str(channelId)][str(userId)] = []
        for text in reversed(possibleSayings_temp):
            textDatabase[str(channelId)][str(userId)].append(text)

    # UPDATE possibleSayings
    if current_impersonate != userId:
        possibleSayings = textDatabase[str(channelId)][str(userId)]
    else:
        await append_possibleSayings(userId, channelId)
    current_impersonate = userId

    # Write to offline database
    with open('data.json', 'w') as fp:
        json.dump(textDatabase, fp, indent=4)

    # Write to offline time
    # subclass JSONEncoder
    class DateTimeEncoder(JSONEncoder):
        # Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

    print("Printing to check how it will look like")
    print(DateTimeEncoder().encode(timeDatabase))
    print("Encode DateTime Object into JSON using custom JSONEncoder")
    with open('time.json', 'w') as fp:
        # json.dump(timeDatabase, fp, indent=4, sort_keys=True, default=str)
        json.dump(timeDatabase, fp, indent=4, cls=DateTimeEncoder)
    # announcement
    await ctx.send(f"Scraped the messages of {user}, on channel {channel.name}.")
    await ctx.guild.me.edit(nick=currentMemberCopying)


@bot.command(name='impersonate')
async def history(ctx, user):
    global possibleSayings
    global currentMemberCopying
    global textDatabase
    global timeDatabase


    # metadata
    userId = int(user[3:-1])
    channelId = ctx.channel.id


    await ctx.send("Obtaining intel. Sit tight.")

    # Identify the message
    await history_helper(ctx, user, userId, ctx.channel, channelId, currentMemberCopying, textDatabase, timeDatabase)


@bot.command(name='impersonate2')
async def history(ctx, user):
    global possibleSayings
    global currentMemberCopying
    global textDatabase
    global timeDatabase

    # Metadata
    userId = int(user[3:-1])
    channel_list = [channel for channel in ctx.guild.channels if isinstance(channel, discord.TextChannel)]

    await ctx.send("Obtaining an extreme amount of intel. Sit tight.")

    # scrape all channels
    for channel in channel_list:
        await history_helper(ctx, user, userId, channel, channel.id, currentMemberCopying, textDatabase, timeDatabase)
    await ctx.send(f"Done. Now I am 100% {user}")


@bot.event
async def on_ready():
    # default possibleSayings
    global possibleSayings

    # reset name to The Impostor
    for guild in bot.guilds:
        await guild.me.edit(nick=bot.user.display_name) # or guild.me.display_name

    # reload_possibleSayings(userId, channelId)
    # get first key in both dict
    # await bot.process_commands()
    print("I'm online!")


@bot.command(name='ramble')
async def talk(ctx):
    try:
        for i in range(0, 10):
            await ctx.send(f"DEBUG {i}" + random.choice(possibleSayings))
    except IndexError:
        await ctx.send("nothing to say yet, plz impersonate")


@bot.command(name='shout')
async def talk(ctx):
    try:
        for i in range(0, 10):
            await ctx.send(f"DEBUG {i} " + random.choice(possibleSayings).upper())
    except IndexError:
        await ctx.send("nothing to say yet, plz impersonate")


@bot.command(name='debug')
async def talk(ctx):
    try:
        for i in range(0, 25):
            try:
                await ctx.send(possibleSayings[i])
            except HTTPException:
                continue
    except IndexError:
        await ctx.send("OUT OF THINGS")


@bot.command(name='talk')
async def talk(ctx):
    try:
        await ctx.send("DEBUG " + random.choice(possibleSayings))
    except IndexError:
        await ctx.send("nothing to say yet, plz impersonate")


@bot.command(name='replyonly')
async def replyonly(ctx):
    global replyOnly
    replyOnly = True
    await ctx.send("Impostor turned to reply only")


@bot.command(name='on')
async def on(ctx):
    global replyOnly
    replyOnly = False
    await ctx.send("Impostor turned to on")


@bot.command(name='info')
async def info(ctx):
    await ctx.send(
        f'List of all commands: \n $impersonate @person - Impersonates the tagged person\n $talk - Forces the Impostor to say something\n $replyonly - Sets the Impostor to only speak when tagged or replied to\n $on - Sets the Impostor to speak when tagged, when replied to, or just randomly')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        await bot.process_commands(message)
        return
    global replyOnly
    global possibleSayings
    saying = ""
    rgen = random.randrange(1, 10)

    # Checks if being tagged
    if "<@!946925871875367002>" in message.content or (
            message.reference is not None and message.reference.resolved.author.id == 946925871875367002):
        saying = getSaying(message, possibleSayings, rgen)
    elif rgen in range(1, 4) and not replyOnly:
        if "?" in message.content:
            saying = getSaying(message, possibleSayings, rgen)
        elif rgen == 2:
            saying = getSaying(message, possibleSayings, rgen)
    if saying != "":
        await message.channel.send(saying)
    await bot.process_commands(message)


def getSaying(message, possibleSayings, rgen):
    saying = random.choice(possibleSayings)
    if "?" in message.content:
        loweredMessage = message.content.lower()
        matches = ["pp", "vhdl", "milk", "sop", "pos", "demorgan"]
        if any(x in loweredMessage for x in matches):
            if rgen in range(1, 5):
                return "Have you tried DeMorgan?"
        saying = random.choice(possibleSayings)
        while "?" in saying:
            saying = random.choice(possibleSayings)
    return saying


@bot.event
async def on_message_delete(message):
    await message.channel.send(message.author.name + " just deleted: " + message.content)
    await bot.process_commands(message)




bot.run(TOKEN)
