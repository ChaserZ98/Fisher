import json
import os
import platform
import asyncio
import random
from sched import scheduler
import time

from traceback import print_exc
import discord
from discord.ext import tasks
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import leetcode_lib as lc


# suppress event loop exception while exiting on windows system
if platform.system() == 'Windows':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

description = "This is a personal bot made by ChaserZ"
bot = commands.Bot(command_prefix='$', description=description)

testChannelID = 979492901019074631

botScheduler = None

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
    global botScheduler
    botScheduler = AsyncIOScheduler()
    botScheduler.start()
    print("Done!")

    print(f"Registered commands and events in {round(time.perf_counter() - time_start, 2)}s")

@tasks.loop(minutes=30.0)
async def status_task() -> None:
    statues = ["fishing", 'fishing a fish', 'fishing a fish fishing', 'fishing a fish fishing a fish', 'fishing a SpongeBob!!!']
    await bot.change_presence(activity=discord.Game(random.choice(statues)))

# exit command
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

# leetcode command
@bot.command(
    aliases=['lc'],
    brief="leetcode command.",
    help='<option>:' +
    "\n\tinit - Equivalent to [channel + start]. Set leetcode channel and start the daily challenge"
    "\n\tjoin - Join the daily coding challenge" +
    "\n\tlist - Show current participants" +
    "\n\tchannel - Set current channel as the channel for the leetcode daily challenge" +
    "\n\tstart - Start the daily challenge" +
    "\n\tstop - Stop the daily challenge" +
    "\n\ttoday - show today's leetcode problem"
    ,
    description="leetcode command description."
)
async def leetcode(ctx, option, *, args=None) -> None:
    if lc.leetcodeChannel is None and (option != 'channel' and option != 'init'):
        await ctx.send("You need to set the channel first.")
        return
    if option is None:
        return
    if option == 'init' and lc.leetcodeChannel is None and args is None:
        lc.leetcodeChannel = ctx.channel
        await ctx.send(f"Set leetcode channel to {ctx.channel}")
        await lc.addLeetcodeSchedule(botScheduler, bot)
    elif option == 'join' and args is None:
        if ctx.author.id in lc.leetcodeParticipantID:
            await ctx.send(ctx.author.mention + " you have already joined the leetcode daily coding challenge!")
        else:
            lc.leetcodeParticipantID[ctx.author.id] = 0
            await ctx.send(ctx.author.mention + " you successfully join the leetcode daily challenge!")
    elif option == 'list' and args is None:
        await lc.showLeetcodeParticipants(bot, lc.leetcodeParticipantID, ctx.channel)
    elif option == 'channel' and args is None:
        lc.leetcodeChannel = ctx.channel
        await ctx.send(f"Set leetcode channel to {ctx.channel}")
    elif option == 'start' and args is None:
        await lc.addLeetcodeSchedule(botScheduler, bot)
    elif option == 'stop' and args is None:
        await lc.removeLeetcodeSchedule(botScheduler)
    elif option == 'today' and args is None:
        await ctx.send(embed=lc.getDailyCodingChallenge())

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return
    
    if message.content.startswith("https://leetcode.com/submissions/detail"):
        userID = message.author.id
        if userID in lc.leetcodeParticipantID and lc.leetcodeParticipantID[userID] == 0:
            await message.add_reaction("✅")
            lc.leetcodeParticipantID[userID] = 1

    await bot.process_commands(message)

try:
    with open("./bot.json", 'r') as token_file:
        TOKEN = json.load(token_file)['token']
    discord_time_start = time.perf_counter()
    bot.run(TOKEN)
except:
    print_exc()
