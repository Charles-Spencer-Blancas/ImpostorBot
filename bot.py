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
global possibleSayings
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


# time reload
# custom Decoder
def DecodeDateTime(empDict):
    for key in empDict:
        empDict[key] = dateutil.parser.parse(empDict[key])
        return empDict


fle = Path('time.json')
fle.touch(exist_ok=True)
f = open(fle)
with open('time.json') as json_file:
    try:
        data = json.load(json_file, object_hook=DecodeDateTime)
        # Print the type of data variable
        print("Type:", type(data))
        timeDatabase = data
        print("first_time")
        print(timeDatabase)
    except JSONDecodeError:
        print("decode_time")
        timeDatabase = dict()
        print(timeDatabase)


@bot.command(name='impersonate')
async def history(ctx, user):
    userId = int(user[3:-1])
    h = await ctx.channel.history(limit=9999).flatten()
    channelId = ctx.channel.id
    global possibleSayings
    global currentMemberCopying
    global textDatabase
    global timeDatabase

    # check if user has been called before
    filteredMessages = []
    if str(userId) in timeDatabase:
        print("current time database", timeDatabase[str(userId)])
        filteredMessages = [
            message for message in h if
            message.author.id == userId and timeDatabase[str(userId)] < message.created_at]
        print("type is here", type(message.created_at))
        print("type is here", type(timeDatabase[str(userId)]))
    else:
        filteredMessages = [
            message for message in h if message.author.id == userId]

    timeDatabase[str(userId)] = filteredMessages[0].created_at
    print("that", timeDatabase[str(userId)])
    print("this", filteredMessages[0].created_at)
    print("this", filteredMessages[0].content)

    currentMemberCopying = filteredMessages[0].author.name
    possibleSayings = [
        message.content for message in filteredMessages]
    print(str(channelId) in textDatabase)
    # Update texts to database
    if str(channelId) in textDatabase:
        if str(userId) in textDatabase[str(channelId)]:
            for text in reversed(possibleSayings):
                textDatabase[str(channelId)][str(userId)].append(text)
        else:
            textDatabase[str(channelId)][str(userId)] = []
            for text in reversed(possibleSayings):
                textDatabase[str(channelId)][str(userId)].append(text)
    else:
        textDatabase[str(channelId)] = dict()
        textDatabase[str(channelId)][str(userId)] = []
        for text in reversed(possibleSayings):
            textDatabase[str(channelId)][str(userId)].append(text)

    # updates offline database
    with open('data.json', 'w') as fp:
        json.dump(textDatabase, fp, indent=4)

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

    await ctx.send(f"Scraped the messages of {user}.")
    await ctx.guild.me.edit(nick=currentMemberCopying)


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
