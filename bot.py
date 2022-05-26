from time import timezone
import discord
from discord.ext import tasks
from discord.ext import commands
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import zoneinfo

with open("./bot.json", 'r') as token_file:
    TOKEN = json.load(token_file)['token']

bot = discord.Client()

async def leetcode_start():
    await bot.wait_until_ready()
    mainChannel = bot.get_channel(978549594877231117)
    await mainChannel.send("func")

async def leetcode_end():
    await bot.wait_until_ready()
    mainChannel = bot.get_channel(978549594877231117)
    await mainChannel.send("func")

@bot.event
async def on_ready():
    mainChannel = bot.get_channel(978549594877231117)
    print(f"{bot.user} has connected to Discord!")
    await mainChannel.send(f"{bot.user.name} has connected to Discord!")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(func, CronTrigger(hour = "12", minute="0", second="0", timezone="America/New_York"))
    scheduler.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

bot.run(TOKEN)
