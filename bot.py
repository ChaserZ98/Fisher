from time import timezone
import discord
from discord.ext import tasks
from discord.ext import commands
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

with open("./bot.json", 'r') as token_file:
    TOKEN = json.load(token_file)['token']

bot = discord.Client()
testChannelID = 979492901019074631

async def leetcode_start():
    await bot.wait_until_ready()
    mainChannel = bot.get_channel(testChannelID)
    await mainChannel.send("func")

async def leetcode_end():
    await bot.wait_until_ready()
    mainChannel = bot.get_channel(testChannelID)
    await mainChannel.send("func")

@bot.event
async def on_ready():
    mainChannel = bot.get_channel(testChannelID)
    print(f"{bot.user} has connected to Discord!")
    await mainChannel.send(f"{bot.user.name} has connected to Discord!")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(leetcode_start, CronTrigger(hour = "12", minute="0", second="0", timezone="America/New_York"))
    scheduler.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content[0] == '$':
        if message.content[1:] == "help":
            await print_help_message(message.channel)
        elif message.content[1:] == "quit":
            await bot.close()
        elif message.content[1:] == "hello":
            await message.channel.send(message.author.mention + " hello!") 

async def print_help_message(channel):
    message = "help message"
    await channel.send(message)


bot.run(TOKEN)
