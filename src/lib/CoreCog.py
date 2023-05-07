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

import discord
from discord.app_commands import locale_str, TranslationContextLocation
from discord.ext import commands

from utils.discord_utils import is_owner

class CoreCog(commands.Cog, name='core'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        
        self.loadable_cogs_dir = 'cogs'
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
            },
            'reload': {
                'en-US': 'reload',
                'zh-CN': '重启'
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
                # No valid subcommand called -> either no subcommand or invalid subcommand
                tokens = ctx.message.content.split(" ") # Split the message into tokens
                
                if len(tokens) > 1:
                    # more than one token, invalid subcommand
                    embed = discord.Embed(
                        description=f"Invalid subcommand: {tokens[1]}",
                        color=0x9C84EF
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    raise commands.CommandError(f"Invalid subcommand: {tokens[1]}")
                
                # No valid subcommand called, default to sync_guild
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

            self.bot.tree.copy_global_to(guild=guild)   # Copy global commands to the guild
            await self.bot.tree.sync(guild=guild)   # Sync the commands to the guild
            
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
            await self.bot.tree.sync()  # Sync the commands globally
            
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
            message = ""
            cog_name = cog_name.lower()
            if cog_name in self.loadable_cogs:
                # valid cog name
                cog_dir = self.loadable_cogs_dir
                cog_file_path = self.loadable_cogs[cog_name]  # get the python file name of the cog
                cog_name = cog_file_path.split(".")[0]  # get the complete cog name
                
                try:
                    await self.bot.load_extension(name=f"{cog_dir}.{cog_file_path}") # load the cog

                    # TODO
                    # update the slash commands
                    # this might trigger the rate limit so it is not implemented yet until I find a better way to do this
                    # guild = ctx.guild
                    # self.bot.tree.copy_global_to(guild=guild)
                    # await self.bot.tree.sync(guild=guild)
                
                except commands.ExtensionAlreadyLoaded as e:
                    message = f"Cog '{cog_name}' cannot be enabled: Cog '{cog_name}' is already enabled."
                    raise e
                except commands.ExtensionNotFound as e:
                    message = f"Cog '{cog_name}' cannot be enabled: Cog '{cog_name}' does not exist."
                    raise e
                except Exception as e:
                    # error when enabling the cog
                    message = f"Cog '{cog_name}' cannot be enabled: {e}"
                    raise e
                else:
                    message = f"Cog '{cog_name}' has been enabled."
                finally:
                    embed = discord.Embed(description=message,color=0x9C84EF)
                    await ctx.send(embed=embed, ephemeral=True)
            else:
                # unknown cog name
                message = f"Cog with name or alias {cog_name} does not exist."
                embed = discord.Embed(description=message,color=0x9C84EF)
                await ctx.send(embed=embed, ephemeral=True)
                raise commands.CommandError(f"Cog '{cog_name}' does not exist")
        
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
            message = ""
            cog_name = cog_name.lower()
            if cog_name in self.loadable_cogs:
                cog_dir = self.loadable_cogs_dir
                cog_file_path = self.loadable_cogs[cog_name]
                cog_name = cog_file_path.split(".")[0]

                try:
                    await self.bot.unload_extension(name=f"{cog_dir}.{cog_file_path}")
                except commands.ExtensionNotLoaded:
                    message = f"Cog '{cog_name}' cannot be disabled: Cog '{cog_name}' is not loaded."
                    raise e
                except Exception as e:
                    message = f"Cog '{cog_name}' cannot be disabled: {e}"
                    raise e
                else:
                    message = f"Cog '{cog_name}' has been disabled."
                finally:
                    embed = discord.Embed(description=message,color=0x9C84EF)
                    await ctx.send(embed=embed, ephemeral=True)
            else:
                message = f"Cog '{cog_name}' does not exist."
                embed = discord.Embed(description=message,color=0x9C84EF)
                await ctx.send(embed=embed, ephemeral=True)
                raise commands.CommandError(f"Cog '{cog_name}' does not exist")
        
        @self.bot.hybrid_command(
                name=locale_str('reload'),
                description='Reload a cog'
        )
        @discord.app_commands.describe(cog_name="additional cog you want to reload")
        @is_owner(self.bot.config['owners'])
        async def reload_cog(ctx : commands.Context, *, cog_name: str):
            message = ""
            cog_name = cog_name.lower()
            if cog_name in self.loadable_cogs:
                cog_dir = self.loadable_cogs_dir
                cog_file_path = self.loadable_cogs[cog_name]
                cog_name = cog_file_path.split(".")[0]

                try:
                    await self.bot.reload_extension(name=f"{cog_dir}.{cog_file_path}")
                except commands.ExtensionNotLoaded as e:
                    message = f"Cog '{cog_name}' cannot be reloaded: Cog '{cog_name}' has not been loaded."
                    raise e
                except Exception as e:
                    message = f"Cog '{cog_name}' cannot be reloaded: {e}"
                    raise e
                else:
                    message = f"Cog '{cog_name}' has been reloaded."
                finally:
                    embed = discord.Embed(description=message,color=0x9C84EF)
                    await ctx.send(embed=embed, ephemeral=True)
            else:
                message = f"Cog '{cog_name}' does not exist."
                embed = discord.Embed(description=message, color=0x9C84EF)
                await ctx.send(embed=embed, ephemeral=True)
                raise commands.CommandError(f"Cog '{cog_name}' does not exist")

async def setup(bot: commands.Bot):
    """Load the cog

    Args:
        bot (commands.Bot): bot instance
    """
    # load the cog
    corecog = CoreCog(bot)
    await bot.add_cog(corecog)

    # update the translation corpus
    bot.tree.translator.update_corpus(TranslationContextLocation.group_name, corecog.localized_group_name)
    bot.tree.translator.update_corpus(TranslationContextLocation.command_name, corecog.localized_command_name)