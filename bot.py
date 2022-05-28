import json
import os
import platform
import asyncio
import random
import time

from traceback import print_exc
import discord
from discord.ext import tasks
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from leetcode import *


if platform.system() == 'Windows':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

description = "This is a test bot by ChaserZ"
bot = commands.Bot(command_prefix='$', description=description)

testChannelID = 979492901019074631

@bot.event
async def on_ready() -> None:
    print(f"Connected to Discord API in {round(time.perf_counter() - discord_time_start, 2)}s")
    print(" Bot Configuration ".center(30, '-'))
    print(f"Logged in bot: {bot.user}")
    print(f"Discord API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"System: {platform.system()} {platform.release()} ({os.name})")
    print("".center(30, '-'))
    mainChannel = bot.get_channel(testChannelID)
    await mainChannel.send(f"{bot.user.name} has connected to Discord!")

    # scheduler
    time_start = time.perf_counter()

    status_task.start()
    
    print(f"Starting scheduler...", end="")
    scheduler = AsyncIOScheduler()
    await addLeetcodeSchedule(scheduler, bot, mainChannel)
    scheduler.start()
    print("Done!")

    print(f"Registered commands and events in {round(time.perf_counter() - time_start, 2)}s")

@tasks.loop(minutes=1.0)
async def status_task() -> None:
    statues = ["fishing", 'fishing a fish', 'fishing a fish fishing', 'fishing a fish fishing a fish', 'fishing a SpongeBob!!!']
    await bot.change_presence(activity=discord.Game(random.choice(statues)))

@commands.has_permissions(administrator=True)
@bot.command(
    aliases=['q', 'exit'],
    brief='logout the bot.',
    help='',
    description="logout the bot."
)
async def quit(ctx, *, args=None) -> None:
    if args:
        return
    print("Shutting down bot...", end='')
    await ctx.send("The bot has been shut down. Bye!")
    await bot.close()
    print("Done!")

@bot.command(
    aliases=['lc'],
    brief="leetcode command.",
    help='leetcode help command',
    description="leetcode command description."
)
async def leetcode(ctx, option=None, *, args=None) -> None:
    if option is None:
        return
    if option == 'join':
        if ctx.author.id in leetcodeParticipantID:
            await ctx.send(ctx.author.mention + " you have already joined the leetcode daily coding challenge!")
        else:
            leetcodeParticipantID[ctx.author.id] = 0
            await ctx.send(ctx.author.mention + " you successfully join the leetcode daily challenge!")
    elif option == 'list':
        await showLeetcodeParticipants(bot, leetcodeParticipantID, ctx.channel)

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    await bot.process_commands(message)

async def print_help_message(channel):
    message = "help message"
    await channel.send(message)

try:
    with open("./bot.json", 'r') as token_file:
        TOKEN = json.load(token_file)['token']
    discord_time_start = time.perf_counter()
    bot.run(TOKEN)
except:
    print_exc()
