import json
import os
import platform
import asyncio
import random
import time
import re

from traceback import print_exc
import discord
import discord.ext.commands
from discord.ext import tasks
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import leetcode_lib as lc


# suppress event loop exception while exiting on windows system
if platform.system() == 'Windows':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

description = "This is a personal bot made by ChaserZ"
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='$',
    description=description,
    intents=intents
)

testChannelID = 979492901019074631

botScheduler = None

@bot.event
async def on_ready() -> None:
    # show configuration
    print(f"Connected to Discord API in {round(time.perf_counter() - discord_time_start, 2)}s")
    print(" Bot Configuration ".center(30, '-'))
    print(f"Logged in bot: {bot.user}")
    print(f"Discord API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"System: {platform.system()} {platform.release()} ({os.name})")
    print("".center(30, '-'))
    mainChannel = bot.get_channel(testChannelID)
    await mainChannel.send(f"{bot.user.name} has connected to Discord!")

    # create data directory and leetcode data directory if not exists
    if not os.path.exists("./data/leetcode"):
        os.makedirs("./data/leetcode")

    lc.synchronize_guild_status()

    time_start = time.perf_counter()

    # start status loop
    status_task.start()
    
    # start scheduler
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
    "\n\tinit - Initialize the coding challenge. This command will overwrite any existed data." +
    "\n\tresume - Initialize the coding challenge based on the stored data." +
    "\n\tclean - Stop the daily coding challenge and clean all data." +
    "\n\tjoin - Join the daily coding challenge." +
    "\n\tquit - Quit the daily coding challenge." +
    "\n\tchannel - Set current channel as the channel for the leetcode daily challenge." +
    "\n\tstart - Start the daily challenge." +
    "\n\tstop - Stop the daily challenge." +
    "\n\tlist - Show current participants." +
    "\n\t[leaderboard|score] - Show history score." +
    "\n\ttoday - Show today's leetcode problem." +
    "\n\t[question|q] <question_id> - Show the leetcode question with the specific question id."
    ,
    description="leetcode command description."
)
async def leetcode(ctx: discord.ext.commands.Context, option=None, *, args: str=None) -> None:
    if (ctx.guild.id not in lc.guild_status or not lc.guild_status[ctx.guild.id]) and (option != 'init' and option != 'resume' and option != 'clean'):
        await ctx.send(
            "You have not initialized the leetcode function in this server.\n" +
            "Please switch to any text channel and enter `$leetcode init` to initialize.\n" +
            "If you want to initialize using your previous data, please enter `$leetcode resume` to resume."
        )
        return
    if option is None:
        return
    if option == 'init' and args is None:
        await lc.initialize(ctx.guild, ctx.channel, botScheduler)
    elif option == 'resume' and args is None:
        if ctx.guild.id in lc.guild_status:
            await lc.resume(ctx.guild, ctx.channel, botScheduler)
        else:
            await ctx.send("You cannot resume since there is no stored data on the server.\nPlease enter `$leetcode init` instead.")
    elif option== 'clean' and args is None:
        if ctx.guild.id in lc.guild_status:
            await lc.clean(ctx.guild, botScheduler)
        await ctx.send("All data has been cleaned.")
    elif option == 'join' and args is None:
        await lc.join(ctx.author, ctx.guild)
    elif option == 'quit' and args is None:
        await lc.quit(ctx.author, ctx.guild)
    elif option == 'channel' and args is None:
        lc.set_leetcode_channel(ctx.guild, ctx.channel)
        await ctx.send(f"Set leetcode channel to {ctx.channel}")
    elif option == 'start' and args is None:
        await lc.add_leetcode_schedule(botScheduler, ctx.guild)
    elif option == 'stop' and args is None:
        await lc.remove_leetcode_schedule(botScheduler, ctx.guild)
    elif option == 'list' and args is None:
        await lc.show_leetcode_participants(ctx.guild)
    elif (option == 'leaderboard' or option == 'score') and args is None:
        await lc.show_leaderboard(ctx.guild)
    elif option == 'today' and args is None:
        await lc.show_today_challenge(ctx.guild)
    elif (option == 'question' or option == 'q') and args:
        args = args.split()
        if len(args) == 1 and args[0].isnumeric():
            question_id = int(args[0])
            if question_id > 0:
                await lc.show_question_by_id(ctx.guild, question_id)
            else:
                await ctx.send("Error: Invalid question id.\nPlease enter `$[lc|leetcode] [q|question] question_id` where `question_id` is a valid number.")
        else:
            await ctx.send("Error: Invalid question id.\nPlease enter `$[lc|leetcode] [q|question] question_id` where `question_id` is a valid number.")
    elif option != None:
        await ctx.send("Unknown option.\nPlease enter `$help [lc|leetcode]` for more info about `leetcode` command.")

@bot.event
async def on_message(message: discord.Message):

    if message.author == bot.user or message.author.bot:
        return
    
    if re.search("^https://leetcode.com/problems/[a-z0-9\-]+/submissions/[0-9]+/?", message.content) and message.guild.id in lc.guild_status and lc.guild_status[message.guild.id]:
        leetcode_role = lc.get_leetcode_role(message.guild)
        daily_report = lc.get_daily_report(message.guild)
        history_score = lc.get_history_score(message.guild)
        if message.author in leetcode_role.members and daily_report[message.author.id] == 0:
            await message.add_reaction("✅")
            daily_report[message.author.id] = 1
            lc.update_daily_report(message.guild, daily_report)

            history_score[message.author.id] += 1
            lc.update_history_score(message.guild, history_score)

    await bot.process_commands(message)

try:
    with open("./bot.json", 'r') as token_file:
        TOKEN = json.load(token_file)['token']
    discord_time_start = time.perf_counter()
    bot.run(TOKEN)
except:
    print_exc()
