#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    CoreCog.py
@Time      :    2023/05/04
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

import os

import discord
from discord.app_commands import locale_str, TranslationContextLocation
from discord.ext import commands

from utils.discord_utils import is_owner

class CoreCog(commands.Cog, name='core'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        
        self.loadable_cog_path = os.path.relpath(
            os.path.realpath(
                os.path.join(os.path.dirname(__file__), '..', 'cogs')
            ),
            os.path.realpath(
                os.path.join(os.path.dirname(__file__), '..')
            )
        )
        self.loadable_cogs = {
            **dict.fromkeys(['lc', 'leetcode'], 'leetcode.LeetcodeCog'),
            **dict.fromkeys(['test'], 'test.TestCog')
        }
        
        self.add_command()

        self.localized_group_name = {
            'sync': {
                'en-US': 'sync',
                'zh-CN': '同步'
            }
        }
        self.localized_command_name = {
            'exit': {
                'en-US': 'exit',
                'zh-CN': '退出'
            },
            'guild': {
                'en-US': 'guild',
                'zh-CN': '单服'
            },
            'globally': {
                'en-US': 'globally',
                'zh-CN': '全服'
            },
            'enable': {
                'en-US': 'enable',
                'zh-CN': '启用'
            },
            'disable': {
                'en-US': 'disable',
                'zh-CN': '禁用'
            }
        }
    
    def add_command(self):
        """Add commands to the bot

        Raises:
            commands.CommandError: error when processing commands
        """

        @self.bot.hybrid_command(
                name=locale_str('exit'),
                description='Exit the bot'
        )
        @is_owner(self.bot.config['owners'])
        async def exit(ctx: commands.Context) -> None:
            """Exit the bot

            Args:
                ctx (commands.Context): context of the command
            """
            if ctx.guild is not None:
                self.bot.logger.info(f"Executed exit command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})")
            else:
                self.bot.logger.info(f"Executed exit command by {ctx.author} (ID: {ctx.author.id}) in DMs")
            
            await ctx.send('Bye')
            await self.bot.close()
        
        @self.bot.hybrid_group(
                name=locale_str('sync'),
                description='Syncronize the slash commands'
        )
        @is_owner(self.bot.config['owners'])
        async def sync(ctx: commands.Context) -> None:
            """Syncronize the slash commands

            Args:
                ctx (commands.Context): context of the command

            Raises:
                commands.CommandError: invalid sync subcommand called
            """
            if ctx.invoked_subcommand is None:
                tokens = ctx.message.content.split(" ")
                if len(tokens) > 1:
                    embed = discord.Embed(
                        description=f"Invalid subcommand: {tokens[1]}",
                        color=0x9C84EF
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    raise commands.CommandError(f"Invalid subcommand: {tokens[1]}")
                await sync_guild(ctx, guild_id=ctx.guild.id)
        
        @sync.command(
                name=locale_str('guild'),
                description='Syncronize slash commands for a specific server, default as the current server'
        )
        @is_owner(self.bot.config['owners'])
        async def sync_guild(
            ctx: commands.Context,
            guild_id: int=commands.parameter(default=lambda ctx: ctx.guild.id)
        ) -> None:
            """Syncronize the slash commands for a specific server

            Args:
                ctx (commands.Context): context of the command
                guild_id (int, optional): ID of the server. Defaults to commands.parameter(default=lambda ctx: ctx.guild.id).
            """
            guild = self.bot.get_guild(guild_id)
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
            embed = discord.Embed(
                description=f"Slash commands have been synchronized in {guild}",
                color=0x9C84EF
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        @sync.command(
                name=locale_str('globally'),
                description="Synchronize slash commands across all servers"
        )
        @is_owner(self.bot.config['owners'])
        async def sync_globally(ctx: commands.Context):
            """Synchronize slash commands across all servers

            Args:
                ctx (commands.Context): context of the command
            """
            await self.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=0x9C84EF
            )
            await ctx.send(embed=embed, ephemeral=True)

        @self.bot.hybrid_command(
                name=locale_str('enable'),
                description='Enable a cog'
        )
        @discord.app_commands.describe(cog_name="additional cog you want to enable")
        @is_owner(self.bot.config['owners'])
        async def enable_cog(ctx : commands.Context, *, cog_name: str):
            """Enable a cog

            Args:
                ctx (commands.Context): context of the command
                cog_name (str): name of the cog

            Raises:
                commands.CommandError: error when enabling the cog
            """
            cog_name = cog_name.lower()
            if cog_name in self.loadable_cogs:
                try:
                    cog = self.loadable_cogs[cog_name]
                    cog_dir = self.loadable_cog_path.replace('/', '.')
                    await self.bot.load_extension(
                        name=f".{cog}",
                        package=cog_dir
                    )
                    
                    embed = discord.Embed(
                        description=f"Cog {cog_name} has been enabled.",
                        color=0x9C84EF
                    )

                    # update the slash commands (might trigger rate limit)
                    # guild = ctx.guild
                    # self.bot.tree.copy_global_to(guild=guild)
                    # await self.bot.tree.sync(guild=guild)

                except Exception as e:
                    embed = discord.Embed(
                        description=f"Cog {cog_name} cannot be enabled: {e}",
                        color=0x9C84EF
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    
                    raise commands.CommandError(f"Cog {cog_name} under package {cog_dir} cannot be enabled: {e}")
            else:
                embed = discord.Embed(
                    description=f"Cog {cog_name} does not exist.",
                    color=0x9C84EF
                )
            await ctx.send(embed=embed, ephemeral=True)
        
        @self.bot.hybrid_command(
                name=locale_str('disable'),
                description='Disable a cog'
        )
        @discord.app_commands.describe(cog_name="additional cog you want to disable")
        @is_owner(self.bot.config['owners'])
        async def disable_cog(ctx : commands.Context, *, cog_name: str):
            """Disable a cog

            Args:
                ctx (commands.Context): context of the command
                cog_name (str): name of the cog

            Raises:
                commands.CommandError: error when disabling the cog
            """
            cog_name = cog_name.lower()
            if cog_name in self.loadable_cogs:
                try:
                    cog = self.loadable_cogs[cog_name]
                    cog_dir = self.loadable_cog_path.replace('/', '.')
                    await self.bot.unload_extension(
                        name=f".{cog}",
                        package=cog_dir
                    )
                    embed = discord.Embed(
                        description=f"Cog {cog_name} has been disabled.",
                        color=0x9C84EF
                    )
                except Exception as e:
                    embed = discord.Embed(
                        description=f"Cog {cog_name} cannot be disabled: {e}",
                        color=0x9C84EF
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    raise commands.CommandError(f"Cog {cog_name} under package {cog_dir} cannot be disabled: {e}")
            else:
                embed = discord.Embed(
                    description=f"Cog {cog_name} does not exist.",
                    color=0x9C84EF
                )
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    corecog = CoreCog(bot)
    await bot.add_cog(corecog)
    bot.tree.translator.update_corpus(TranslationContextLocation.group_name, corecog.localized_group_name)
    bot.tree.translator.update_corpus(TranslationContextLocation.command_name, corecog.localized_command_name)