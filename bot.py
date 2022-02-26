import pandas as pd
from discord.ext import commands
from dotenv import load_dotenv
import os
import random


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
global bot
bot = commands.Bot(command_prefix='$')

global currentMemberCopying
global possibleSayings


@bot.command(name='getHistoryOf')
async def history(ctx, user):
    userId = int(user[3:-1])
    h = await ctx.channel.history(limit=9999).flatten()
    global possibleSayings
    global currentMemberCopying

    filteredMessages = [
        message for message in h if message.author.id == userId]

    currentMemberCopying = filteredMessages[0].author.name
    possibleSayings = [
        message.content for message in filteredMessages]

    await ctx.send(f"Scraped the messages of {user}.")
    await ctx.guild.me.edit(nick=currentMemberCopying)


@ bot.command(name='talk')
async def talk(ctx):
    await ctx.send(random.choice(possibleSayings))

# client.run(TOKEN)
bot.run(TOKEN)
