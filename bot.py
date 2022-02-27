import json
from json import JSONDecodeError
import dateutil
from discord.ext import commands
# from dotenv import load_dotenv
import os
import random
from pathlib import Path
import datetime
from json import JSONEncoder
import dateutil.parser

# load_dotenv()
# TOKEN = os.getenv('DISCORD_TOKEN2')
TOKEN = os.environ['TOKEN']
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



async def history_helper(ctx, user, userId, channel, channelId, possibleSayings, currentMemberCopying, textDatabase, timeDatabase):
    # fetch messages after if date exist
    h = []
    if str(channelId) in timeDatabase:
        if str(userId) in timeDatabase[str(channelId)]:
            h = await channel.history(limit=9999, after=timeDatabase[str(channelId)][str(userId)]).flatten()
    else:
        h = await channel.history(limit=9999).flatten()
    # check if user has been called before
    filteredMessages = []
    filteredMessages = [message for message in h if message.author.id == userId]
    # check if channel has ever been scraped
    if str(channelId) in timeDatabase:
        if str(userId) in timeDatabase[str(channelId)]:
            print("current time database", timeDatabase[str(channelId)][str(userId)])
            if filteredMessages is not None:
                filteredMessages = [message for message in filteredMessages if timeDatabase[str(channelId)][str(userId)] < message.created_at]
    else:
        timeDatabase[str(channelId)] = dict()
   # check if there are new messages
    if len(filteredMessages) == 0:
        return
    # update time
    timeDatabase[str(channelId)][str(userId)] = filteredMessages[0].created_at
    # to rename bot
    currentMemberCopying = filteredMessages[0].author.name
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
    # new possibleSayings after scrape
    possibleSayings = textDatabase[str(channelId)][str(userId)]
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
    await ctx.send("Obtaining intel. Sit tight.")
    global possibleSayings
    global currentMemberCopying
    global textDatabase
    global timeDatabase
    # Identify the message
    userId = int(user[3:-1])
    channelId = ctx.channel.id
    await history_helper(ctx, user, userId, ctx.channel, channelId, possibleSayings, currentMemberCopying, textDatabase, timeDatabase)

@bot.command(name='impersonate2')
async def history(ctx, user):
    await ctx.send("Obtaining an extreme amount intel. Sit tight.")
    global possibleSayings
    global currentMemberCopying
    global textDatabase
    global timeDatabase
    # Identify the message
    userId = int(user[3:-1])
    channel_list = [channel for channel in ctx.guild.channels if isinstance(channel, discord.TextChannel)]
    # scrape all channels
    for channel in channel_list:
        await history_helper(ctx, user, userId, channel, channel.id, possibleSayings, currentMemberCopying, textDatabase, timeDatabase)
    await ctx.send(f"Done. Now I am 100% {user}")

@bot.command(name='talk')
async def talk(ctx):
    await ctx.send(random.choice(possibleSayings))


@bot.command(name='replyOnly')
async def replyonly(ctx):
    global replyOnly
    replyOnly = True
    await ctx.send("Tag me when you need me. Or reply to something I said.")


@bot.command(name='on')
async def on(ctx):
    global replyOnly
    replyOnly = False
    await ctx.send("The Impostor is now listening.")


@bot.event
async def on_ready():
    print("I'm online!")
    # await bot.process_commands()


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
