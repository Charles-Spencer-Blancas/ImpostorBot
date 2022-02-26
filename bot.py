import pandas as pd
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import HashTable

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
global bot
bot = commands.Bot(command_prefix='$')

global currentMemberCopying
global possibleSayings
global textDatabase
textDatabase = HashTable.HashTable(50)


@bot.command(name='getHistoryOf')
async def history(ctx, user):
    userId = int(user[3:-1])
    h = await ctx.channel.history(limit=9999).flatten()
    global possibleSayings
    global currentMemberCopying
    global textDatabase

    filteredMessages = [
        message for message in h if message.author.id == userId]

    currentMemberCopying = filteredMessages[0].author.name
    possibleSayings = [
        message.content for message in filteredMessages]
    textDatabase.set_val(currentMemberCopying, possibleSayings)
    print(textDatabase.get_val(currentMemberCopying))

    await ctx.send(f"Scraped the messages of {user}.")
    await ctx.guild.me.edit(nick=currentMemberCopying)


@ bot.command(name='talk')
async def talk(ctx):
    await ctx.send(random.choice(possibleSayings))

# client.run(TOKEN)
bot.run(TOKEN)