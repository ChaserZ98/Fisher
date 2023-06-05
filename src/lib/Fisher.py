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
from lib.Exceptions import ModuleCommandException
from utils.discord_utils import is_owner

class Fisher(commands.Bot):
    def __init__(
            self,
            intents: discord.Intents,
            logger: logging.Logger,
            config: dict,
            bot_status: list,
            data_dir: str,
    ):
        super().__init__(command_prefix=config['prefix'], description=config['description'], intents=intents)
        
        self.logger = logger
        
        self.config = config
        
        self.bot_status = bot_status

        self.data_dir = data_dir

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
    def bot_status(self) -> list:
        return self._bot_status
    
    @bot_status.setter
    def bot_status(self, val: list):
        self._bot_status = val
    
    @property
    def data_dir(self) -> str:
        return self._data_dir
    
    @data_dir.setter
    def data_dir(self, val: str):
        self._data_dir = val
    
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
    
    async def on_ready(self):
        self.logger.info(f"Bot {self.user.name} is ready to use")
        main_channel = self.get_channel(self.config['dev_channel_id'])
        await main_channel.send(f"{self.user.name} has connected to Discord!")
        
        self.status_task.start()
        self.logger.info("Bot status loop started")

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
    
    @tasks.loop(minutes=30.0)
    async def status_task(self):
        await self.change_presence(activity=discord.Game(random.choice(self.bot_status)))

    async def on_command_completion(self, ctx: Context):
        if ctx.message.content:
            command = ctx.message.content
            command_type = "prefix command"
        else:
            command = ctx.prefix + ctx.command.qualified_name + " " + " ".join(map(lambda item: f"{str(item[0])}:{str(item[1])}", ctx.kwargs.items()))
            command_type = "slash command"
        
        if ctx.guild is not None:
            self.logger.info(f"Executed {command_type} '{command}' in {ctx.guild.name} (Guild ID: {ctx.guild.id}) by {ctx.author} (User ID: {ctx.author.id})")
        else:
            self.logger.info(f"Executed {command_type} '{command}' by {ctx.author} (User ID: {ctx.author.id}) in DMs")
    
    async def on_command_error(self, ctx: Context, exception) -> None:
        if ctx.message.content:
            command = ctx.message.content
            command_type = "Prefix command"
        else:
            command = ctx.prefix + ctx.command.qualified_name + " " + " ".join(map(lambda item: f"{str(item[0])}:{str(item[1])}", ctx.kwargs.items()))
            command_type = "Slash command"
        
        if ctx.guild is not None:
            self.logger.warning(f"User: {ctx.author} (ID: {ctx.author.id}) Guild: {ctx.guild.name} (ID: {ctx.guild.id}) {command_type}: '{command}' Exception: {exception}")
        else:
            self.logger.warning(f"User: {ctx.author} (ID: {ctx.author.id}) {command_type}: '{command}' Exception: {exception}")
        
        if isinstance(exception, ModuleCommandException):
            user_message = f"An error occurred while executing the command \n'{command}'\nError: {exception.user_message}"
        else:
            user_message = f"An internal error occurred while executing the command \n'{command}'"

        await ctx.send(user_message, ephemeral=True)

        # if isinstance(exception, commands.CommandOnCooldown):
        #     minutes, seconds = divmod(exception.retry_after, 60)
        #     hours, minutes = divmod(minutes, 60)
        #     hours = hours % 24

