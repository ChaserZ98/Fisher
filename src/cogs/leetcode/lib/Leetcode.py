#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    Leetcode.py
@Time      :    2023/06/03
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

from datetime import datetime
import json
import os
import re
import requests
import shutil
from typing import Tuple

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from discord.ext import commands

from cogs.leetcode.lib.LeetcodeGuild import LeetcodeGuild
from lib.Exceptions import ModuleCommandException
from utils.discord_utils import set_role

class Leetcode:
    __slots__ = ('url', 'EMBED_FIELD_VALUE_LIMIT', 'guilds', 'scheduler', 'data_dir_path', 'module_data_dir_name', 'daily_coding_challenge_cache', 'leetcode_session')
    def __init__(
        self,
        data_dir_path: str,
        module_data_dir_name: str = 'leetcode',
        config_file_name: str = 'config.json',
        url: str = 'https://leetcode.com'
    ):
        self.data_dir_path = data_dir_path
        self.module_data_dir_name = module_data_dir_name

        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        
        self.url = url
        self.EMBED_FIELD_VALUE_LIMIT = 1024

        self.daily_coding_challenge_cache = None
        self.get_daily_coding_challenge(use_cache=False)

        self.leetcode_session = requests.Session()
        self.leetcode_session.cookies.update({'LEETCODE_SESSION': os.getenv('LEETCODE_SESSION')})
        
        self.guilds = {}
        for guild in os.listdir(data_dir_path):
            guild_module_data_dir_path = os.path.join(data_dir_path, guild, module_data_dir_name)
            if os.path.exists(guild_module_data_dir_path):
                try:
                    self.guilds[int(guild)] = LeetcodeGuild.from_file(guild_module_data_dir_path, config_file_name)
                except Exception as e:
                    print(f'Error loading guild {guild}: {e}')
    
    async def initialize(
            self,
            guild : discord.Guild,
            leetcode_channel_id : int,
            config_file_name : str = 'config.json'
    ):
        guild_id = guild.id
        leetcode_role = await self.set_leetcode_role(guild)
        leetcode_role_id = leetcode_role.id

        guild_module_data_dir_path = os.path.join(self.data_dir_path, str(guild_id), self.module_data_dir_name)
        if os.path.exists(guild_module_data_dir_path):
            shutil.rmtree(guild_module_data_dir_path)
        os.makedirs(guild_module_data_dir_path)

        self.guilds[guild_id] = LeetcodeGuild(guild_module_data_dir_path, leetcode_role_id, leetcode_channel_id, config_file_name)

        message = self.add_leetcode_schedule(guild)
        return message
    
    def resume(self, guild: discord.Guild, config_file_name: str = 'config.json'):
        guild_module_data_dir_path = os.path.join(self.data_dir_path, str(guild.id), self.module_data_dir_name)
        if not os.path.exists(guild_module_data_dir_path):
            raise ModuleCommandException(
                log_message=f'Guild {guild.id} has not been initialized.',
                user_message='Guild has not been initialized.',
                module_name=self.module_data_dir_name
            )

        self.guilds[guild.id] = LeetcodeGuild.from_file(guild_module_data_dir_path, config_file_name)
        
        self.remove_leetcode_schedule(guild)
        self.add_leetcode_schedule(guild)

        return "Guild has been resumed."
    
    async def clean(self, ctx: commands.Context):
        guild = ctx.guild
        if guild.id not in self.guilds:
            raise ModuleCommandException(
                log_message=f'Guild {guild.id} has not been initialized.',
                user_message='Guild has not been initialized.',
                module_name=self.module_data_dir_name
            )
        
        # remove role
        leetcode_role = guild.get_role(self.guilds[guild.id].config['leetcode_role_id'])
        if leetcode_role:
            await leetcode_role.delete()

        # remove scheduled job
        self.remove_leetcode_schedule(guild)

        # remove data
        guild_module_data_dir_path = os.path.join(self.data_dir_path, str(guild.id), self.module_data_dir_name)
        if os.path.exists(guild_module_data_dir_path):
            shutil.rmtree(guild_module_data_dir_path)
        del self.guilds[guild.id]

        return "Leetcode module data has been cleaned."
    
    def add_leetcode_schedule(self, guild: discord.Guild):
        self.add_time_schedule(guild, 'start')
        self.add_time_schedule(guild, 'remind')
        self.add_time_schedule(guild, 'end')

        self.guilds[guild.id].config['daily_challenge_status'] = True

        message = f"Leetcode daily coding challenge job all set.\n" + \
            f"Daily timezone: {self.guilds[guild.id].config['timezone']}\n" + \
            f"Daily start time: {':'.join(self.guilds[guild.id].config['start_time'].values())}\n" + \
            f"Daily remind time: {':'.join(self.guilds[guild.id].config['remind_time'].values())}\n" + \
            f"Daily end time: {':'.join(self.guilds[guild.id].config['end_time'].values())}"
        return message

    def add_time_schedule(self, guild: discord.Guild, time_type: str) -> Tuple[str, str]:
        leetcode_channel = guild.get_channel(self.guilds[guild.id].config['leetcode_channel_id'])
        leetcode_role = guild.get_role(self.guilds[guild.id].config['leetcode_role_id'])

        if self.scheduler.get_job(f"leetcode {time_type} {guild.id}"):
            self.scheduler.remove_job(f"leetcode {time_type} {guild.id}")
        
        if time_type == 'start':
            self.scheduler.add_job(
                self.leetcode_start,
                CronTrigger(
                    **self.guilds[guild.id].config['start_time'],
                    timezone=self.guilds[guild.id].config['timezone']
                ),
                args=(leetcode_channel, leetcode_role),
                misfire_grace_time=None,
                id=f'leetcode start {guild.id}'
            )
        elif time_type == 'remind':
            self.scheduler.add_job(
                self.leetcode_remind,
                CronTrigger(
                    **self.guilds[guild.id].config['remind_time'],
                    timezone=self.guilds[guild.id].config['timezone']
                ),
                args=(guild, self.guilds[guild.id].daily_report, leetcode_channel),
                misfire_grace_time=None,
                id=f'leetcode remind {guild.id}'
            )
        elif time_type == 'end':
            self.scheduler.add_job(
                self.leetcode_end,
                CronTrigger(
                    **self.guilds[guild.id].config['end_time'],
                    timezone=self.guilds[guild.id].config['timezone']
                ),
                args=(guild, leetcode_channel),
                misfire_grace_time=None,
                id=f'leetcode end {guild.id}'
            )
        else:
            raise ModuleCommandException(
                log_message=f'Time type {time_type} is not supported.',
                user_message=f'Time type {time_type} is not supported.',
                module_name=self.module_data_dir_name
            )
        
        user_message = f"The leetcode daily coding challenge's {time_type} time has been set successfully."
        log_message = f"The leetcode daily coding challenge's {time_type} time for guild {guild.id} has been set successfully."
        return user_message, log_message

    async def leetcode_start(self, leetcode_channel: discord.TextChannel, leetcode_role: discord.Role):
        embed = self.get_daily_coding_challenge(use_cache=False)
        await leetcode_channel.send(embed=embed)
        await leetcode_channel.send(f"The new daily coding challenge has released! {leetcode_role.mention}")
    
    async def leetcode_remind(self, guild: discord.Guild, daily_report: dict, leetcode_channel: discord.TextChannel):
        unfinishedCount = 0
        unfinishedUser = ""
        for user_id, value in daily_report.items():
            user = guild.get_member(user_id)
            if value == 0:
                unfinishedCount += 1
                unfinishedUser += user.mention
        content = "Today's leetcode daily coding challenge will be end soon. You still have some time to complete it."
        if unfinishedCount > 0:
            content += "\n" + unfinishedUser
        await leetcode_channel.send(content)
    
    async def leetcode_end(self, guild: discord.Guild, leetcode_channel: discord.TextChannel):
        completedUser = ""
        completedCount = 0
        unfinishedUser = ""
        unfinishedCount = 0
        for user_id, value in self.guilds[guild.id].daily_report.items():
            user = guild.get_member(user_id)
            if value == 1:
                completedCount += 1
                completedUser += f"\n{completedCount}. {user.name}"
                self.guilds[guild.id].daily_report[user_id] = 0
            else:
                unfinishedCount += 1
                unfinishedUser += f"\n{unfinishedCount}. {user.name}"
        content = "Today's leetcode daily coding challenge has ended."
        if completedCount > 0:
            content += f"\nCompleted participants (total: {completedCount}):" + completedUser
        if unfinishedCount > 0:
            content += f"\nUnfinished participants (total: {unfinishedCount}):" + unfinishedUser
        await leetcode_channel.send(content)

    def remove_leetcode_schedule(self, guild: discord.Guild):
        self.remove_time_schedule(guild, 'start')
        self.remove_time_schedule(guild, 'remind')
        self.remove_time_schedule(guild, 'end')

        self.guilds[guild.id].config['daily_challenge_status'] = False
        
        user_message = "The leetcode daily coding challenge has stopped successfully."
        log_message = f"The leetcode daily coding challenge for guild {guild.id} has stopped successfully."
        return user_message, log_message
    
    def remove_time_schedule(self, guild: discord.Guild, time_type: str) -> Tuple[str, str]:
        if self.scheduler.get_job(f"leetcode {time_type} {guild.id}"):
            self.scheduler.remove_job(f"leetcode {time_type} {guild.id}")
        
        user_message = f"The leetcode daily coding challenge's {time_type} time scheduler has been removed successfully."
        log_message = f"The leetcode daily coding challenge's {time_type} time scheduler for guild {guild.id} has been removed successfully."
        return user_message, log_message

    async def join(self, ctx: commands.Context):
        guild = ctx.guild
        user = ctx.author
        leetcode_role = guild.get_role(int(self.guilds[guild.id].config['leetcode_role_id']))
        if user.id in self.guilds[guild.id].daily_report:
            user_message = f'{user.mention} you have already joined the daily leetcode challenge.'
            log_message = f'User {user} ({user.id}) tried to join the daily leetcode challenge in guild {guild.id} but already joined.'
        else:
            await user.add_roles(leetcode_role)

            self.guilds[guild.id].daily_report[user.id] = 0
            self.guilds[guild.id].history_score[user.id] = 0

            user_message = f'{user.mention} you successfully join the leetcode daily coding challenge!'
            log_message = f'User {user} ({user.id}) successfully joined the daily leetcode challenge in guild {guild.id}.'
        return user_message, log_message

    async def quit(self, ctx: commands.Context) -> Tuple[str, str]:
        guild = ctx.guild
        user = ctx.author
        leetcode_role = guild.get_role(int(self.guilds[guild.id].config['leetcode_role_id']))
        if user.id in self.guilds[guild.id].daily_report:
            await user.remove_roles(leetcode_role)
            del self.guilds[guild.id].daily_report[user.id]
            del self.guilds[guild.id].history_score[user.id]
            user_message = f'{user.mention} you successfully quit the leetcode daily coding challenge!'
            log_message = f'User {user} ({user.id}) successfully quit the daily leetcode challenge in guild {guild.id}.'
        else:
            user_message = f'{user.mention} you have not joined the daily leetcode challenge yet.'
            log_message = f'User {user} ({user.id}) tried to quit the daily leetcode challenge in guild {guild.id} but not joined.'
        return user_message, log_message

    def submit_solution(self, guild: discord.Guild, user: discord.Member, url: str) -> Tuple[str, discord.Embed, str]:
        # check if guild has been initialized
        guild_module_data_dir_path = os.path.join(self.data_dir_path, str(guild.id), self.module_data_dir_name)
        if not os.path.exists(guild_module_data_dir_path):
            raise ModuleCommandException(
                log_message=f'Guild {guild.id} has not been initialized.',
                user_message='Guild has not been initialized.',
                module_name=self.module_data_dir_name
            )
        # check if user joined
        if user.id not in self.guilds[guild.id].daily_report:
            user_message = f'You have not joined the daily leetcode challenge yet.'
            log_message = f'User {user} ({user.id}) tried to submit their solution in guild {guild.id} but not joined.'
            return user_message, None, log_message
        
        # check url
        valid_url = re.search("^https://leetcode.com/problems/([a-z0-9\-]+)/submissions/([0-9]+)/?", url)
        if valid_url:
            problem_name = valid_url.group(1)
            submission_id = int(valid_url.group(2))
        else:
            raise ModuleCommandException(
                log_message=f"Invalid submission url '{url}' from user {user} ({user.id}) in guild {guild.id}.",
                user_message=f"Invalid submission url '{url}'\nPlease check the url and try again.",
                module_name=self.module_data_dir_name
            )
        
        # check problem name
        if problem_name != self.daily_coding_challenge_cache['question']['titleSlug']:
            raise ModuleCommandException(
                log_message=f"Invalid problem name '{problem_name}' from user {user.id} in guild {guild.id} while the correct problem name is '{self.daily_coding_challenge_cache['question']['titleSlug']}'.",
                user_message=f"Incorrect daily problem. Please check the problem and try again. Today's leetcode problem is '{self.daily_coding_challenge_cache['question']['title']}'.",
                module_name=self.module_data_dir_name
            )
        
        user_embed = self.get_submission(submission_id)

        if self.guilds[guild.id].daily_report[user.id] == 1:
            user_message = f'You have already submitted your solution today.'
            log_message = f'User {user} ({user.id}) tried to submit their solution in guild {guild.id} but already submitted.'
            return user_message, None, log_message
        
        self.guilds[guild.id].daily_report[user.id] += 1
        self.guilds[guild.id].history_score[user.id] += 1
        user_message = f'Solution received!'
        log_message = f'User {user} ({user.id}) successfully submitted their solution in guild {guild.id}.'
        
        return user_message, user_embed, log_message

    async def set_leetcode_role(self, guild: discord.Guild) -> discord.Role:
        leetcode_role = await set_role(
            guild=guild,
            name='Leetcode',
            color=discord.Color.orange(),
            hoist=False,
            mentionable=False,
            reason="leetcode daily coding challenge member"
        )
        return leetcode_role

    def set_channel(self, ctx: commands.Context) -> str:
        guild = ctx.guild
        leetcode_channel = ctx.channel
        self.guilds[guild.id].config["leetcode_channel_id"] = leetcode_channel.id
        message = f'Set leetcode channel to {leetcode_channel.mention}'
        return message
    
    def set_timezone(self, guild: discord.Guild, timezone: str) -> str:
        self.guilds[guild.id].config["timezone"] = timezone
        self.remove_leetcode_schedule(guild)
        self.add_leetcode_schedule(guild)
        user_message = f"Set timezone to '{timezone}' successfully."
        log_message = f"Set timezone to '{timezone}' in guild {guild.id} successfully."
        return user_message, log_message
    
    def set_time(self, guild: discord.Guild, time_type: str, hour: int, minute: int, second: int) -> str:
        self.guilds[guild.id].config[f"{time_type}_time"] = {
            "hour": f"{hour:02d}",
            "minute": f"{minute:02d}",
            "second": f"{second:02d}"
        }
        self.remove_leetcode_schedule(guild)
        self.add_leetcode_schedule(guild)
        user_message = f"Set {time_type} time to {hour:02d}:{minute:02d}:{second:02d} successfully."
        log_message = f"Set {time_type} time to {hour:02d}:{minute:02d}:{second:02d} in guild {guild.id} successfully."
        return user_message, log_message

    def get_participants(self, guild: discord.Guild):
        leetcode_role = guild.get_role(self.guilds[guild.id].config['leetcode_role_id'])

        if len(leetcode_role.members) == 0:
            return "No participants yet."
        
        message = "Current participants"

        names = ""

        for index, member in enumerate(leetcode_role.members):
            names += f"\n{index + 1}. {member.name}"
        message += f" (total participants: {len(leetcode_role.members)}): {names}"

        return message

    def get_leaderboard(self, guild: discord.Guild):
        history_score = self.guilds[guild.id].history_score
        if len(history_score) == 0:
            return "No participants yet."

        rank = sorted(history_score.items(), key=lambda x: x[1], reverse=True)

        message = "Leaderboard"

        names = ""

        for index, (user_id, score) in enumerate(rank):
            user = guild.get_member(int(user_id))
            names += f"\n{index + 1}. {user.name} ({score})"
        message += f" (total participants: {len(rank)}): {names}"

        return message

    def get_daily_coding_challenge(self, use_cache: bool = True) -> discord.Embed:
        if use_cache and self.daily_coding_challenge_cache:
            result = self.daily_coding_challenge_cache
        else:
            post_url = self.url + "/graphql"
            data = {
                "query": "query questionOfToday \
                    {\
                        activeDailyCodingChallengeQuestion\
                            {\
                                date\
                                userStatus\
                                link\
                                question{\
                                    questionId\
                                    questionFrontendId\
                                    title\
                                    titleSlug\
                                    acRate\
                                    difficulty\
                                    freqBar\
                                    likes\
                                    dislikes\
                                    content\
                                    similarQuestions\
                                    isFavor\
                                    paidOnly: isPaidOnly\
                                    status\
                                    hasVideoSolution\
                                    hasSolution\
                                    topicTags {name id slug}\
                            }\
                    }\
                }",
                "operationName": "questionOfToday"
            }
            # header = {'content-type': 'application/json'}
            result = requests.post(post_url, json=data).json()['data']['activeDailyCodingChallengeQuestion']
            self.daily_coding_challenge_cache = result
        question_date = result['date']
        question_id = result['question']['questionFrontendId']
        title = result['question']['title']
        question_link = self.url + result['link']
        ac_rate = result['question']['acRate']
        difficulty = result['question']['difficulty']
        likes = result['question']['likes']
        dislikes = result['question']['dislikes']
        content = result['question']['content']
        paid_only = result['question']['paidOnly']
        has_solution = result['question']['hasSolution']
        solution_link = question_link + "solution/"
        topic_tags = result['question']['topicTags']
        similar_questions = json.loads(result['question']['similarQuestions'])

        embed = discord.Embed()

        embed.title = f"🏆 Leetcode Daily Coding Challenge ({question_date})"

        # problem field
        problem_field = {}
        if paid_only:
            problem_field['name'] = f"Problem {question_id} 💰"
        else:
            problem_field['name'] = f"Problem {question_id}"
        problem_field['value'] = f"[{title}]({question_link}) ({difficulty})"
        if has_solution:
            problem_field['value'] += f" [Solution]({solution_link})"
        problem_field['inline'] = False
        embed.add_field(
            name=problem_field['name'],
            value=problem_field['value'],
            inline=problem_field['inline']
        )

        # acceptance rate field
        acceptance_field = {
            'name': f"Acceptance",
            'value': f"{round(ac_rate, 2)}%",
            'inline': True
        }
        embed.add_field(
            name=acceptance_field['name'],
            value=acceptance_field['value'],
            inline=acceptance_field['inline']
        )

        # like field
        like_field = {
            'name': f"👍 Like",
            'value': likes,
            'inline': True
        }
        embed.add_field(
            name=like_field['name'],
            value=like_field['value'],
            inline=like_field['inline']
        )

        # dislike field
        dislike_field = {
            'name': f"👎 Dislike",
            'value': dislikes,
            'inline': True
        }
        embed.add_field(
            name=dislike_field['name'],
            value=dislike_field['value'],
            inline=dislike_field['inline']
        )

        # related topic field
        topic_field_value = ""
        for i in range(len(topic_tags)):
            value = f"[{topic_tags[i]['name']}]({self.url}/tag/{topic_tags[i]['slug']}/)"
            if len(topic_field_value) + len(value) > self.EMBED_FIELD_VALUE_LIMIT:
                break
            topic_field_value += value
            if i != len(topic_tags) - 1:
                topic_field_value += ', '
        embed.add_field(
            name="Related topics",
            value=topic_field_value,
            inline=False
        )

        # similar questions field
        similar_field_value = ""
        for i in range(len(similar_questions)):
            value = f"[{similar_questions[i]['title']}]({self.url}/problems/{similar_questions[i]['titleSlug']}/) ({similar_questions[i]['difficulty']})"
            if len(similar_field_value) + len(value) > self.EMBED_FIELD_VALUE_LIMIT:
                break
            similar_field_value += value
            if i != len(similar_questions) - 1:
                similar_field_value += '\n'
        if len(similar_questions) > 0:
            embed.add_field(
                name='Similar questions',
                value=similar_field_value,
                inline=False
            )

        return embed

    def get_question_by_id(self, question_id : int) -> discord.Embed:
        get_url = self.url + "/api/problems/all/"
        result = requests.get(get_url).json()
        problems = list(
            map(
                lambda x: {
                    "frontend_question_id": x['stat']['frontend_question_id'],
                    "title_slug": x['stat']['question__title_slug']
                },
                sorted(
                    result['stat_status_pairs'],
                    key=lambda x: x['stat']['frontend_question_id']
                )
            )
        )
        if question_id > len(problems):
            return None
        title_slug = problems[question_id - 1]['title_slug']
        post_url = self.url + "/graphql"
        data = {
            "operationName": "questionData",
            "variables": {
                "titleSlug": title_slug
            },
            "query":
            "query questionData($titleSlug: String!){\
                question(titleSlug: $titleSlug) {\
                    questionId\
                    questionFrontendId\
                    title\
                    titleSlug\
                    acRate\
                    difficulty\
                    freqBar\
                    likes\
                    dislikes\
                    content\
                    similarQuestions\
                    isFavor\
                    paidOnly: isPaidOnly\
                    status\
                    hasVideoSolution\
                    hasSolution\
                    topicTags {name id slug}\
                }\
            }"
        }
        result = requests.post(post_url, json=data).json()['data']['question']
        question_id = result['questionFrontendId']
        title = result['title']
        question_link = self.url + "/problems/" + result['titleSlug'] + "/"
        ac_rate = result['acRate']
        difficulty = result['difficulty']
        likes = result['likes']
        dislikes = result['dislikes']
        content = result['content']
        paid_only = result['paidOnly']
        has_solution = result['hasSolution']
        solution_link = question_link + "solution/"
        topics_tags = result['topicTags']
        similar_questions = json.loads(result['similarQuestions'])

        embed = discord.Embed()

        # embed title & description
        if paid_only:
            embed.title = f"Leetcode Problem {question_id} 💰"
        else:
            embed.title = f"Leetcode Problem {question_id}"
        embed.description = f"[{title}]({question_link}) ({difficulty})"
        if has_solution:
            embed.description += f" [Solution]({solution_link})"

        # acceptance rate field
        acceptance_field = {'name': f"Acceptance", 'value': f"{round(ac_rate, 2)}%", 'inline': True}
        embed.add_field(
            name=acceptance_field['name'],
            value=acceptance_field['value'],
            inline=acceptance_field['inline']
        )

        # like field
        like_field = {
            'name': f"👍 Like",
            'value': likes,
            'inline': True
        }
        embed.add_field(
            name=like_field['name'],
            value=like_field['value'],
            inline=like_field['inline']
        )

        # dislike field
        dislike_field = {
            'name': f"👎 Dislike",
            'value': dislikes,
            'inline': True
        }
        embed.add_field(
            name=dislike_field['name'],
            value=dislike_field['value'],
            inline=dislike_field['inline']
        )

        # related topic field
        topic_field_value = ""
        for i in range(len(topics_tags)):
            value = f"[{topics_tags[i]['name']}]({self.url}/tag/{topics_tags[i]['slug']}/)"
            if len(topic_field_value) + len(value) > self.EMBED_FIELD_VALUE_LIMIT:
                break
            topic_field_value += value
            if i != len(topics_tags) - 1:
                topic_field_value += ', '
        embed.add_field(
            name="Related topics",
            value=topic_field_value,
            inline=False
        )

        # similar questions field
        similar_field_value = ""
        for i in range(len(similar_questions)):
            value = f"[{similar_questions[i]['title']}]({self.url}/problems/{similar_questions[i]['titleSlug']}/) ({similar_questions[i]['difficulty']})"
            if len(similar_field_value) + len(value) > self.EMBED_FIELD_VALUE_LIMIT:
                break
            similar_field_value += value
            if i != len(similar_questions) - 1:
                similar_field_value += '\n'
        if len(similar_questions) > 0:
            embed.add_field(
                name='Similar questions',
                value=similar_field_value,
                inline=False
            )

        return embed
    
    def get_info(self, guild: discord.Guild):
        guild_module_data_dir_path = os.path.join(self.data_dir_path, str(guild.id), self.module_data_dir_name)
        if not os.path.exists(guild_module_data_dir_path):
            raise ModuleCommandException(
                log_message=f'Guild {guild.id} has not been initialized.',
                user_message='Guild has not been initialized.',
                module_name=self.module_data_dir_name
            )
        
        leetcode_role = guild.get_role(self.guilds[guild.id].config['leetcode_role_id'])
        leetcode_channel = guild.get_channel(self.guilds[guild.id].config['leetcode_channel_id'])
        daily_challenge_status = self.guilds[guild.id].config['daily_challenge_status']
        daily_challenge_timezone = self.guilds[guild.id].config['timezone']
        start_time = self.guilds[guild.id].config['start_time']
        end_time = self.guilds[guild.id].config['end_time']
        remind_time = self.guilds[guild.id].config['remind_time']

        user_message = f'Leetcode role: {leetcode_role.mention}'
        user_message += f'\nLeetcode channel: {leetcode_channel.mention}'
        user_message += f'\nTotal members: {len(leetcode_role.members)}'
        if daily_challenge_status:
            user_message += f'\nDaily timezone: {daily_challenge_timezone}'
            user_message += f'\nDaily start time: {":".join(start_time.values())}'
            user_message += f'\nDaily end time: {":".join(end_time.values())}'
            user_message += f'\nDaily remind time: {":".join(remind_time.values())}'
        else:
            user_message += '\nDaily challenge: disabled'
        
        return user_message

    def get_submission(self, submission_id: int) -> discord.Embed:
        post_url = self.url + "/graphql"
        data = {
            "operationName": "submissionDetails",
            "query":
            "query submissionDetails($submissionId: Int!){\
                submissionDetails(submissionId: $submissionId) {\
                    runtime\
                    runtimeDisplay\
                    runtimePercentile\
                    runtimeDistribution\
                    memory\
                    memoryDisplay\
                    memoryPercentile\
                    memoryDistribution\
                    code\
                    timestamp\
                    statusCode\
                    user {\
                        username\
                        profile {realName userAvatar}\
                    }\
                    lang {\
                        name\
                        verboseName\
                    }\
                    question {\
                        questionId\
                        questionFrontendId\
                        title\
                        difficulty\
                        paidOnly: isPaidOnly\
                    }\
                    notes\
                    topicTags {\
                        tagId\
                        slug\
                        name\
                    }\
                    runtimeError\
                    compileError\
                    lastTestcase\
                }\
            }",
            "variables": {
                "submissionId": submission_id
            },
        }
        response = self.leetcode_session.post(post_url, json=data)
        
        if not response:
            raise ModuleCommandException(
                log_message=f'Failed to get submission {submission_id}: Status code: {response.status_code} Reason: {response.reason}.',
                user_message='Failed to get submission due to request error.',
                module_name=self.module_data_dir_name
            )
        
        result = response.json()
        
        if 'errors' in result:
            raise ModuleCommandException(
                log_message=f'Failed to get submission {submission_id} due to error: {result["errors"][0]["message"]}.',
                user_message=f'Failed to get submission due to invalid submission id {submission_id}.',
                module_name=self.module_data_dir_name
            )
        
        data = result['data']['submissionDetails']

        question_id = data['question']['questionFrontendId']
        question_title = data['question']['title']
        question_link = self.url + self.daily_coding_challenge_cache['link']
        question_difficulty = data['question']['difficulty']
        question_paid_only = data['question']['paidOnly']
        submission_runtime_display = data['runtimeDisplay']
        submission_runtime_percentile = data['runtimePercentile']
        submission_memory_display = data['memoryDisplay']
        submission_memory_percentile = data['memoryPercentile']
        submission_author = data['user']['username']
        submission_language = data['lang']['verboseName']
        submission_time = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        submission_code = data['code']

        embed = discord.Embed()

        embed.set_author(
            name=f'{submission_author}',
            icon_url=data['user']['profile']['userAvatar']
        )

        embed.title = f'✍️ Leetcode Daily Coding Challenge Submission'

        embed.url = f'{self.url}/submissions/detail/{submission_id}/'

        problem_field = {
            'name': f"Problem {question_id} 💰" if question_paid_only else f"Problem {question_id}",
            'value': f"[{question_title}]({question_link}) ({question_difficulty})",
            'inline': False
        }
        embed.add_field(**problem_field)

        # runtime field
        runtime_field = {
            'name': f"Runtime",
            'value': f"{submission_runtime_display} (Beats: {str(int(submission_runtime_percentile * 100) / 100) + '%' if submission_runtime_percentile else submission_runtime_percentile})",
            'inline': True
        }
        embed.add_field(**runtime_field)

        # memory field
        memory_field = {
            'name': f"Memory",
            'value': f"{submission_memory_display} (Beats: {str(int(submission_memory_percentile * 100) / 100) + '%' if submission_memory_percentile else submission_memory_percentile})",
            'inline': True
        }
        embed.add_field(**memory_field)

        support_highlight = {
            'python3': 'python',
            'python': 'python',
            'javascript': 'javascript',
            'java': 'java',
            'c++': 'cpp',
            'c': 'c',
            'c#': 'csharp',
            'sql': 'sql',
            'mysql': 'sql',
            'go': 'go',
            'ruby': 'ruby',
            'swift': 'swift',
            'scala': 'scala',
            'kotlin': 'kotlin',
            'rust': 'rust',
            'php': 'php',
            'typescript': 'typescript',
            'r': 'r',
            'bash': 'bash',
            'shell': 'bash',
            'html': 'html',
            'css': 'css',
            'scala': 'scala'
        }

        highlight_type = support_highlight.get(submission_language.lower(), submission_language.lower())

        # code field
        code_field = {
            'name': f"Submission code ({submission_language})",
            'value': f"```{highlight_type}\n{submission_code}```",
            'inline': False
        }
        embed.add_field(**code_field)

        embed.set_footer(text=f'{submission_time} | {submission_id}')

        return embed
        