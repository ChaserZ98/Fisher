import logging
import os
import platform
import random
import time

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context

class Fisher(commands.Bot):
    def __init__(
            self,
            intents: discord.Intents,
            logger: logging.Logger,
            config: dict
    ):
        super().__init__(command_prefix=config['prefix'], description=config['description'], intents=intents)
        
        self.logger = logger
        self.config = config

    @property
    def logger(self) -> logging.Logger:
        return self._logger
    
    @logger.setter
    def logger(self, val: logging.Logger):
        self._logger = val
    
    @property
    def config(self) -> dict:
        return self._config
    
    @config.setter
    def config(self, val: dict):
        self._config = val
    
    @property
    def start_time(self) -> float:
        return self._start_time
    
    @start_time.setter
    def start_time(self, val: float):
        self._start_time = val
    
    async def on_ready(self):
        self.logger.info(f"Connected to Discord API in {round(time.perf_counter() - self.start_time, 2)}s")
        self.logger.info(" Bot Configuration ".center(60, '-'))
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("".center(60, '-'))

        main_channel = self.get_channel(self.config['dev_channel_id'])
        await main_channel.send(f"{self.user.name} has connected to Discord!")

        self.status_task.start()
        self.logger.info("Bot status loop started")

        self.add_core_commands()
        self.logger.info("Bot core commands loaded")

        if self.config["sync_commands_globally"]:
            self.logger.info("Syncing commands globally...")
            await self.tree.sync()
            self.logger.info("Successfully Sync commands globally")
    
    @tasks.loop(minutes=30.0)
    async def status_task(self):
        statues = ["fishing", 'fishing a fish', 'fishing a fish fishing', 'fishing a fish fishing a fish', 'fishing a SpongeBob!!!']
        await self.change_presence(activity=discord.Game(random.choice(statues)))

    async def on_command_completion(self, ctx: Context):
        full_command_name = ctx.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if ctx.guild is not None:
            self.logger.info(f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})")
        else:
            self.logger.info(f"Executed {executed_command} command by {ctx.author} (ID: {ctx.author.id}) in DMs")
    
    async def on_command_error(self, ctx: Context, exception) -> None:
        print(2, ctx.interaction, exception)
        # if isinstance(exception, commands.CommandOnCooldown):
        #     minutes, seconds = divmod(exception.retry_after, 60)
        #     hours, minutes = divmod(minutes, 60)
        #     hours = hours % 24
    
    def add_core_commands(self):
        @self.hybrid_command(name='hello', description='hello world')
        async def hello(ctx: Context):
            print(ctx.interaction)
            print(ctx.message.content)

