#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    Fisher.py
@Time      :    2023/03/29
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

import logging
import os
import platform
import random
import time

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context

from lib.Translator import FisherTranslator
from utils.discord_utils import is_owner

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
        self.statues = ["fishing", 'fishing a fish', 'fishing a fish fishing', 'fishing a fish fishing a fish', 'fishing a SpongeBob!!!']

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

    async def setup_hook(self):
        self.logger.info(f"Connected to Discord API in {round(time.perf_counter() - self.start_time, 2)}s")
        self.logger.info(" Bot Configuration ".center(60, '-'))
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("".center(60, '-'))

        if self.config['use_translator']:
            await self.tree.set_translator(FisherTranslator())
            self.logger.info("Command tree translator set")

        await self.load_extension('lib.CoreCog')
        self.logger.info("Bot core commands loaded")

        self.logger.info("Loading default cogs...")
        for cog in self.config['extensions']['cogs']:
            cog_name = cog.split(".")[0]
            await self.load_extension(name=f"cogs.{cog}")
            self.logger.info(f"Cog '{cog_name}' loaded")
        self.logger.info("Default cogs loading complete")

        if self.config["sync_commands_globally"]:
            self.logger.info("Syncing commands globally...")
            await self.tree.sync()
            self.logger.info("Successfully Sync commands globally")
    
    async def on_ready(self):
        self.logger.info(f"Bot {self.user.name} is ready to use")
        main_channel = self.get_channel(self.config['dev_channel_id'])
        await main_channel.send(f"{self.user.name} has connected to Discord!")
        
        self.status_task.start()
        self.logger.info("Bot status loop started")
    
    @tasks.loop(minutes=30.0)
    async def status_task(self):
        await self.change_presence(activity=discord.Game(random.choice(self.statues)))

    async def on_command_completion(self, ctx: Context):
        full_command_name = ctx.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if ctx.guild is not None:
            self.logger.info(f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})")
        else:
            self.logger.info(f"Executed {executed_command} command by {ctx.author} (ID: {ctx.author.id}) in DMs")
    
    async def on_command_error(self, ctx: Context, exception) -> None:
        command = ctx.message.content if ctx.message.content else ctx.command.qualified_name + " ".join(ctx.command.params.values())
        self.logger.warning(f"User: {ctx.author} (ID: {ctx.author.id}) Guild: {ctx.guild.name} (ID: {ctx.guild.id}) Command: '{ctx.message.content}' Exception: {exception}")
        # if isinstance(exception, commands.CommandOnCooldown):
        #     minutes, seconds = divmod(exception.retry_after, 60)
        #     hours, minutes = divmod(minutes, 60)
        #     hours = hours % 24

