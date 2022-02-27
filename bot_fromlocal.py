import json
from json import JSONDecodeError


from discord.ext import commands
from dotenv import load_dotenv
import os
import random
from pathlib import Path


load_dotenv()
TOKEN = os.environ['TOKEN']
global bot
bot = commands.Bot(command_prefix='$')

global currentMemberCopying
global possibleSayings
global textDatabase
global timeDatabase
global replyOnly

replyOnly = False
# global filteredMessages

# textDatabase = HashTable.HashTable(50)

# dict implementation
# textDatabase = dict()

# file system
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

timeDatabase = dict()

timeDatabase = dict()

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
    if userId in timeDatabase:
        filteredMessages = [
            message for message in h if
            message.author.id == userId and timeDatabase[userId] < message.created_at]
    else:
        filteredMessages = [
            message for message in h if message.author.id == userId]

    timeDatabase[userId] = filteredMessages[0].created_at
    print("this", filteredMessages[0].created_at)
    print("this", filteredMessages[0].content)
    print("that", timeDatabase[userId])
    currentMemberCopying = filteredMessages[0].author.name
    possibleSayings = [
        message.content for message in filteredMessages]

    # Update texts to database
    if channelId in textDatabase:
        if userId in textDatabase[channelId]:
            for text in reversed(possibleSayings):
                textDatabase[channelId][userId].append(text)
        else:
            textDatabase[channelId][userId] = []
            for text in reversed(possibleSayings):
                textDatabase[channelId][userId].append(text)
    else:
        textDatabase[channelId] = dict()
        textDatabase[channelId][userId] = []
        for text in reversed(possibleSayings):
            textDatabase[channelId][userId].append(text)


    with open('data.json', 'w') as fp:
        json.dump(textDatabase, fp)

    # json_object = json.dumps(textDatabase, indent=4)
    # print(json_object)

    # DEBUG
    # print(filteredMessages[0].created_at)
    # print(filteredMessages[-1].created_at)
    # print(filteredMessages[-1].created_at < filteredMessages[0].created_at)

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
async def on_message(message):
    if message.author == bot.user:
        await bot.process_commands(message)
        return
    global replyOnly
    global possibleSayings
    rgen = random.randrange(1, 10)
    # Checks if being tagged
    if "<@!946925871875367002>" in message.content:
        await message.channel.send(random.choice(possibleSayings))
        # await bot.process_commands(message)

    elif message.reference is not None and message.reference.resolved.author.id == 946925871875367002:
        await message.channel.send(random.choice(possibleSayings))
        # await bot.process_commands(message)

    # High chance to reply to question
    elif "?" in message.content and rgen in range(1, 4) and not replyOnly:
        saying = random.choice(possibleSayings)
        while "?" in saying:
            saying = random.choice(possibleSayings)
        await message.channel.send(saying)
        # await bot.process_commands(message)

    # Random replies
    elif rgen == 2 and not replyOnly:
        await message.channel.send(random.choice(possibleSayings))
        # await bot.process_commands(message)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print("I'm online!")
    # await bot.process_commands()


# def getSaying():

@bot.event
async def on_message_delete(message):
    await message.channel.send(message.author.name + " just deleted: " + message.content)
    await bot.process_commands(message)


# client.run(TOKEN)
bot.run(TOKEN)