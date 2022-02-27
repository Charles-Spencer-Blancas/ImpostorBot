#import pandas as pd
from discord.ext import commands
#from dotenv import load_dotenv Uncomment when final
import os
import random
import discord
# client = discord.Client()
#load_dotenv() Uncomment when final
#TOKEN = os.getenv('DISCORD_TOKEN') Uncomment when final
TOKEN = os.environ['TOKEN'] # For repl, remove for final
global bot
bot = commands.Bot(command_prefix='$',activity=discord.Game(name='enter $info for help'))

global currentMemberCopying
global possibleSayings
global textDatabase
global replyOnly
replyOnly = False

@bot.command(name='impersonate')
async def history(ctx, user):
    await ctx.send("Obtaining intel. Sit tight.")
    userId = int(user[3:-1])
    h = await ctx.channel.history(limit=9999).flatten()
    global possibleSayings
    global currentMemberCopying
    global textDatabase

    filteredMessages = [
        message for message in h if message.author.id == userId]

    currentMemberCopying = filteredMessages[0].author.name
    possibleSayings = [
        message.content for message in filteredMessages if "$" not in message.content]
    #textDatabase.set_val(currentMemberCopying, possibleSayings)
    #print(textDatabase.get_val(currentMemberCopying))

    await ctx.send(f"I am now {user}.")
    await ctx.guild.me.edit(nick=currentMemberCopying)

@bot.command(name='talk')
async def talk(ctx):
  await ctx.send(random.choice(possibleSayings))
  
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
  await ctx.send(f'List of all commands: \n $impersonate @person - Impersonates the tagged person\n $talk - Forces the Impostor to say something\n $replyonly - Sets the Impostor to only speak when tagged or replied to\n $on - Sets the Impostor to speak when tagged, when replied to, or just randomly')

@bot.event
async def on_message(message):
  if message.author == bot.user:
    await bot.process_commands(message)    
    return
  global replyOnly
  global possibleSayings
  saying = ""
  rgen = random.randrange(1,10)

  # Checks if being tagged
  if "<@!946925871875367002>" in message.content or (message.reference is not None and message.reference.resolved.author.id == 946925871875367002):
    saying = getSaying(message, possibleSayings, rgen)
  elif rgen in range(1,4) and not replyOnly:
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
      if rgen in range(1,5): 
        return "Have you tried DeMorgan?"
    saying = random.choice(possibleSayings)
    while "?" in saying:
      saying = random.choice(possibleSayings)
  return saying

@bot.event
async def on_message_delete(message):
  await message.channel.send(message.author.name + " just deleted: "+ message.content)
  await bot.process_commands(message)

@bot.event
async def on_ready():
  print("I'm online!")

bot.run(TOKEN)