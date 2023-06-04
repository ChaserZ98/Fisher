#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    LeetcodeCog.py
@Time      :    2023/06/03
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

from typing import Type, Union

import discord
from discord.app_commands import TranslationContextLocation
from discord.ext import commands
from pytz import all_timezones

from cogs.leetcode.lib.Leetcode import Leetcode

class LeetcodeCog(commands.Cog, name='leetcode'):
    def __init__(
        self,
        bot: commands.Bot,
        url: str='https://leetcode.com',
        module_data_dir_name: str='leetcode',
        module_guild_config_file_name: str='config.json'
    ):
        self.bot = bot

        self.leetcode_module = Leetcode(
            self.bot.data_dir,
            module_data_dir_name,
            module_guild_config_file_name,
            url
        )

        self.localized_group_name = {
            'leetcode': {
                'en-US': 'leetcode',
                'zh-CN': 'leetcode'
            },
            'set': {
                'en-US': 'set',
                'zh-CN': '设置'
            }
        }

        self.localized_command_name = {
            'init': {
                'en-US': 'init',
                'zh-CN': '初始化'
            },
            'resume': {
                'en-US': 'resume',
                'zh-CN': '恢复'
            },
            'clean': {
                'en-US': 'clean',
                'zh-CN': '清除'
            },
            'join': {
                'en-US': 'join',
                'zh-CN': '加入'
            },
            'quit': {
                'en-US': 'quit',
                'zh-CN': '退出'
            },
            'channel': {
                'en-US': 'channel',
                'zh-CN': '频道'
            },
            'start': {
                'en-US': 'start',
                'zh-CN': '开始'
            },
            'stop': {
                'en-US': 'stop',
                'zh-CN': '停止'
            },
            'list': {
                'en-US': 'list',
                'zh-CN': '列表'
            },
            'leaderboard': {
                'en-US': 'leaderboard',
                'zh-CN': '排行榜'
            },
            'score': {
                'en-US': 'score',
                'zh-CN': '分数'
            },
            'today': {
                'en-US': 'today',
                'zh-CN': '今日'
            },
            'question': {
                'en-US': 'question',
                'zh-CN': '题目'
            },
            'info': {
                'en-US': 'info',
                'zh-CN': '信息'
            },
            'set': {
                'en-US': 'set',
                'zh-CN': '设置'
            },
            'timezone': {
                'en-US': 'timezone',
                'zh-CN': '时区'
            },
            'time': {
                'en-US': 'time',
                'zh-CN': '设置时间'
            },
            'submit': {
                'en-US': 'submit',
                'zh-CN': '提交'
            },
            'get_submission': {
                'en-US': 'get_submission',
                'zh-CN': '获取提交'
            },
            'help': {
                'en-US': 'help',
                'zh-CN': '帮助'
            },
            'test': {
                'en-US': 'test',
                'zh-CN': '测试'
            }
        }

        self.add_command()

    def add_command(self):

        @self.bot.hybrid_group(
                name='leetcode',
                aliases=['lc'],
                brief='leetcode command.',
                description='leetcode command description.',
                help='<option>:' +
                    "\n\thelp - Show this help message." + 
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
                    "\n\t[question|q] <question_id> - Show the leetcode question with the specific question id." + 
                    "\n\tget_submission <submission_id> - Get the submission result with the specific submission id." +
                    '\n\tinfo - Show the leetcode module information.' + 
                    '\n\tsubmit <url> - Submit the leetcode solution.' +
                    '\n\tset <option> <value> - Set the leetcode module option.',
        )
        async def leetcode(ctx: commands.Context) -> None:
            if ctx.invoked_subcommand is None:
                tokens = ctx.message.content.split(' ')
                if len(tokens) > 1:
                    await ctx.send(f'Unknown leetcode subcommand: {tokens[1]}', ephemeral=True)
                    raise commands.CommandError(f"Invalid subcommand: {tokens[1]}")
                await help(ctx)
        
        @leetcode.command(
            name='help',
            brief='help command.',
            description='show help message.'
        )
        async def help(ctx: commands.Context) -> None:
            await ctx.defer(ephemeral=True)
            embed = discord.Embed(
                title='Leetcode Help',
                description='Leetcode module help message.',
                color=discord.Color.blue()
            )
            embed.add_field(
                name='Command List',
                value='```' + '\n'.join([f'{command.name} - {command.description}' for command in leetcode.commands]) + '```',
                inline=False
            )

            await ctx.send(embed=embed, ephemeral=True)
            self.bot.logger.info(f'Help message sent in guild {ctx.guild.id}.')

        @leetcode.command(
            name='init',
            brief='init command.',
            description='initialize the leetcode module in the current guild.'
        )
        async def init(ctx: commands.Context) -> None:
            message = await self.leetcode_module.initialize(ctx.guild, ctx.channel.id)
            self.bot.logger.info(f'Leetcode module initialized in guild {ctx.guild.id}.')
            await ctx.send('Leetcode module initialized.\n' + message)
        
        @leetcode.command(
            name='resume',
            brief='resume command.',
            description='resume the leetcode module in the current guild.'
        )
        async def resume(ctx: commands.Context) -> None:
            message = await self.leetcode_module.resume(ctx.guild)
            self.bot.logger.info(f'Leetcode module resumed in guild {ctx.guild.id}.')
            await ctx.send(message, ephemeral=True)

        @leetcode.command(
            name='clean',
            brief='clean command.',
            description='clean the leetcode module in the current guild.'
        )
        async def clean(ctx: commands.Context) -> None:
            message = await self.leetcode_module.clean(ctx)
            self.bot.logger.info(f'Leetcode module data cleaned in guild {ctx.guild.id}.')
            await ctx.send(message, ephemeral=True)

        @leetcode.command(
            name='join',
            brief='join command.',
            description='join the daily coding challenge.'
        )
        async def join(ctx : commands.Context) -> None:
            user_message, log_message = await self.leetcode_module.join(ctx)
            self.bot.logger.info(log_message)
            await ctx.send(user_message, ephemeral=True)
        
        @leetcode.command(
            name='quit',
            brief='quit command.',
            description='quit the daily coding challenge.'
        )
        async def quit(ctx : commands.Context) -> None:
            user_message, log_message = await self.leetcode_module.quit(ctx)
            self.bot.logger.info(log_message)
            await ctx.send(user_message, ephemeral=True)
        
        @leetcode.command(
            name='channel',
            brief='channel command.',
            description='set current channel as the channel for the leetcode daily challenge.'
        )
        async def channel(ctx : commands.Context) -> None:
            message = await self.leetcode_module.set_channel(ctx)
            await ctx.send(message, ephemeral=True)
        
        @leetcode.command(
            name='start',
            brief='start command.',
            description='start the daily challenge.'
        )
        async def start(ctx : commands.Context) -> None:
            message = await self.leetcode_module.add_leetcode_schedule(ctx.guild)
            await ctx.send(message)
        
        @leetcode.command(
            name='stop',
            brief='stop command.',
            description='stop the daily challenge.'
        )
        async def stop(ctx : commands.Context) -> None:
            user_message, log_message = await self.leetcode_module.remove_leetcode_schedule(ctx.guild)
            self.bot.logger.info(log_message)
            await ctx.send(user_message)
        
        @leetcode.command(
            name='list',
            aliases=['ls'],
            brief='list command.',
            description='show current participants.'
        )
        async def show_participants(ctx : commands.Context) -> None:
            await ctx.send(self.leetcode_module.get_participants(ctx.guild))

        @leetcode.command(
            name='leaderboard',
            aliases=['score'],
            brief='leaderboard command.',
            description='show history score.'
        )
        async def show_leaderboard(ctx : commands.Context) -> None:
            await ctx.send(self.leetcode_module.get_leaderboard(ctx.guild))

        @leetcode.command(
            name='today',
            brief='today command.',
            description='show today\'s leetcode problem.'
        )
        async def today(ctx: commands.Context) -> None:
            await ctx.send(embed=self.leetcode_module.get_daily_coding_challenge(), ephemeral=True)

        @leetcode.command(
            name='question',
            aliases=['q'],
            brief='question command.',
            description='show the leetcode question with the specific question id.'
        )
        async def question(ctx : commands.Context, question_id: int) -> None:
            await ctx.send(embed=self.leetcode_module.get_question_by_id(question_id))

        @leetcode.command(
            name='get_submission',
            brief='get submission command.',
            description='get the leetcode submission with the specific submission id.'
        )
        async def get_submission(ctx : commands.Context, submission_id: int) -> None:
            await ctx.send(embed=self.leetcode_module.get_submission(submission_id))

        @leetcode.command(
            name='info',
            brief='info command.',
            description='show the leetcode module information.'
        )
        async def info(ctx : commands.Context) -> None:
            await ctx.send(self.leetcode_module.get_info(ctx.guild))

        @leetcode.command(
            name='submit',
            brief='submit command.',
            description='submit the leetcode solution.'
        )
        async def submit(ctx : commands.Context, url: str) -> None:
            user_message, user_embed, log_message = self.leetcode_module.submit_solution(ctx.guild, ctx.author, url)
            self.bot.logger.info(log_message)
            await ctx.send(user_message)
            if user_embed is not None:
                leetcode_channel = self.bot.get_channel(self.leetcode_module.guilds[ctx.guild.id].config['leetcode_channel_id'])
                await leetcode_channel.send(embed=user_embed)

        @leetcode.group(
            name='set',
            brief='set command.',
            description='set configuration of leetcode module'
        )
        async def set_config(ctx: commands.Context) -> None:
            if ctx.invoked_subcommand is None:
                tokens = ctx.message.content.split(' ')
                if len(tokens) > 1:
                    await ctx.send(f'Unknown set subcommand: {tokens[1]}', ephemeral=True)
                    raise commands.CommandError(f"Invalid subcommand: {tokens[1]}")
                await ctx.send_help(ctx.command)

        async def timezone_autocomplete(ctx: commands.Context, current: str):
            return [discord.app_commands.Choice(name=tz, value=tz) for tz in all_timezones if current.lower().replace(' ', '') in tz.lower().replace('_', '')][:25]

        @set_config.command(
            name='timezone',
            brief='timezone command.',
            description='set timezone for the daily challenge.'
        )
        @discord.app_commands.autocomplete(timezone=timezone_autocomplete)
        async def set_timezone(ctx: commands.Context, timezone: str) -> None:
            user_message, log_message = await self.leetcode_module.set_timezone(ctx.guild, timezone)
            self.bot.logger.info(log_message)
            await ctx.send(user_message, ephemeral=True)

        async def time_type_autocomplete(ctx: commands.Context, current: str):
            return [
                discord.app_commands.Choice(name='start', value='start'),
                discord.app_commands.Choice(name='end', value='end'),
                discord.app_commands.Choice(name='remind', value='remind')
            ]

        @set_config.command(
            name='time',
            brief='set daily challenge time.',
            description='set different time for the daily challenge.'
        )
        @discord.app_commands.describe(
            time_type='start/end/remind',
            hour='hour of a day (0-23)',
            minute='minute of a hour (0-59)',
            second='second of a minute (0-59)'
        )
        @discord.app_commands.autocomplete(time_type=time_type_autocomplete)
        async def set_time(ctx: commands.Context, time_type: str, hour: discord.app_commands.Range[int, 0, 23], minute: discord.app_commands.Range[int, 0, 59] = 0, second: discord.app_commands.Range[int, 0, 59] = 0) -> None:
            user_message, log_message = self.leetcode_module.set_time(ctx.guild, time_type, hour, minute, second)
            self.bot.logger.info(log_message)
            await ctx.send(user_message)


async def setup(bot: commands.Bot):
    leetcodecog = LeetcodeCog(bot)
    await bot.add_cog(leetcodecog)

    # update the translation corpus
    bot.tree.translator.update_corpus(
        TranslationContextLocation.group_name,
        leetcodecog.localized_group_name
    )
    bot.tree.translator.update_corpus(
        TranslationContextLocation.command_name,
        leetcodecog.localized_command_name
    )
