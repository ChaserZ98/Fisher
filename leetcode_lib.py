import os
import shutil
import requests
import json
import pickle

from apscheduler.triggers.cron import CronTrigger
import discord

data_directory = "./data"
leetcode_data_directory = "leetcode"

leetcode_role_id_file_name = "leetcode_role.txt"

daily_report_file_name = "leetcode_participants.txt"

history_score_file_name = "leetcode_history_score.txt"

leetcode_channel_file_name = "leetcode_channel.txt"

timezone="America/New_York"
start_time = {
    'hour': "08",
    'minute': "00",
    'second': "00"
}
end_time = {
    'hour': "23",
    'minute': "59",
    'second': "59"
}

guild_status = {}

def synchronize_guild_status():
    global data_directory, leetcode_data_directory, guild_status
    for path in os.listdir(os.path.join(data_directory, leetcode_data_directory)):
        if os.path.isdir(os.path.join(data_directory, leetcode_data_directory, path)):
            guild_status[int(path)] = False

def check_server_data(guild: discord.Guild):
    return os.path.exists(os.path.join(data_directory, leetcode_data_directory, str(guild.id)))

def serialize(data, path):
    with open(path, 'wb') as file:
        pickle.dump(data, file)

def deserialize(path):
    with open(path, 'rb') as file:
        return pickle.load(file)

def synchronize_daily_report_member(guild: discord.Guild):
    role = get_leetcode_role(guild)
    old_daily_report = get_daily_report(guild)
    member_ids = [member.id for member in role.members]
    new_daily_report = {}
    for user_id in member_ids:
        if user_id in old_daily_report:
            new_daily_report[user_id] = old_daily_report[user_id]
        else:
            new_daily_report[user_id] = 0
    update_daily_report(guild, new_daily_report)

def synchronize_history_score(guild: discord.Guild):
    role = get_leetcode_role(guild)
    old_history_score = get_history_score(guild)
    member_ids = [member.id for member in role.members]
    new_history_score = {}
    for user_id in member_ids:
        if user_id in member_ids:
            new_history_score[user_id] = old_history_score[user_id]
        else:
            new_history_score[user_id] = 0
    update_history_score(guild, new_history_score)

def update_daily_report(guild: discord.Guild, daily_report: dict):
    global data_directory, leetcode_data_directory, daily_report_file_name
    serialize(
        daily_report,
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            daily_report_file_name
        )
    )

def get_daily_report(guild: discord.Guild) -> dict:
    global data_directory, leetcode_data_directory, daily_report_file_name
    return deserialize(
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            daily_report_file_name
        )
    )

def update_history_score(guild: discord.Guild, history_score: dict):
    global data_directory, leetcode_data_directory, history_score_file_name
    serialize(
        history_score,
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            history_score_file_name
        )
    )

def get_history_score(guild: discord.Guild) -> dict:
    global data_directory, leetcode_data_directory, history_score_file_name
    return deserialize(
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            history_score_file_name
        )
    )

def set_leetcode_channel(guild: discord.Guild, channel: discord.TextChannel):
    global data_directory, leetcode_data_directory, leetcode_channel_file_name
    serialize(
        channel.id,
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            leetcode_channel_file_name
        )
    )

def get_leetcode_channel(guild: discord.Guild):
    global data_directory, leetcode_data_directory, leetcode_channel_file_name
    channelID = deserialize(
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            leetcode_channel_file_name
        )
    )
    return guild.get_channel(channelID)

async def set_leetcode_role(guild: discord.Guild) -> discord.Role:
    global data_directory, leetcode_data_directory, leetcode_role_id_file_name
    leetcode_role = await set_role(
        guild,
        name="Leetcode",
        color=discord.Color.orange(),
        hoist=False,
        mentionable=False,
        reason="leetcode daily coding challenge member"
    )
    serialize(
        leetcode_role.id, 
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            leetcode_role_id_file_name
        )
    )
    return leetcode_role

def get_leetcode_role(guild: discord.Guild) -> discord.Role:
    global data_directory, leetcode_data_directory, leetcode_role_id_file_name
    leetcode_role_id = deserialize(
        os.path.join(
            data_directory,
            leetcode_data_directory,
            str(guild.id),
            leetcode_role_id_file_name
        )
    )
    return guild.get_role(leetcode_role_id)

async def set_role(guild: discord.Guild, name: str, color: discord.Color=discord.Color.default(), hoist: bool=False, mentionable: bool=False, reason: str=None) -> discord.Role:
    for role in guild.roles:
        if role.name == name:
            await role.delete()
            break
    return await guild.create_role(
        name=name,
        color=color,
        hoist=hoist,
        mentionable=mentionable,
        reason=reason
    )

async def initialize(guild: discord.Guild, channel: discord.TextChannel, scheduler):

    # create server data directory
    global data_directory, leetcode_data_directory
    server_directory = os.path.join(data_directory, leetcode_data_directory, str(guild.id))
    if check_server_data(guild):
        shutil.rmtree(server_directory)
    os.makedirs(server_directory)
    
    # set channel
    set_leetcode_channel(guild, channel)

    # create leetcode role
    leetcode_role = await set_leetcode_role(guild)

    # create daily report file
    global daily_report_file_name
    daily_report = {}
    for user in leetcode_role.members:
        daily_report[user] = 0
    serialize(daily_report, os.path.join(server_directory, daily_report_file_name))

    # create score history file
    global history_score_file_name
    serialize(daily_report, os.path.join(server_directory, history_score_file_name))

    # start leetcode job
    await add_leetcode_schedule(scheduler, guild)

    # add record in guild status
    global guild_status
    guild_status[guild.id] = True

    await channel.send("Initialization complete!")

async def resume(guild: discord.Guild, channel: discord.TextChannel, scheduler):
    # syncronize daily report member data
    synchronize_daily_report_member(guild)

    # syncronize history score
    synchronize_history_score(guild)

    # set leetcode channel
    set_leetcode_channel(guild, channel)
    
    # start leetcode job
    await add_leetcode_schedule(scheduler, guild)

    guild_status[guild.id] = True

    await channel.send("Resume complete!")

async def clean(guild: discord.Guild, scheduler):
    
    # delete leetcode role
    leetcode_role = get_leetcode_role(guild)
    if leetcode_role:
        await leetcode_role.delete()

    # delete schedule job
    await remove_leetcode_schedule(scheduler, guild)
    
    # delete data
    global data_directory, leetcode_data_directory
    if check_server_data(guild):
        shutil.rmtree(
            os.path.join(
                data_directory,
                leetcode_data_directory,
                str(guild.id)
            )
        )
    # delete record in guild status
    synchronize_guild_status()

async def join(user: discord.Member, guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    leetcode_role = get_leetcode_role(guild)

    synchronize_daily_report_member(guild)
    daily_report = get_daily_report(guild)

    synchronize_history_score(guild)
    history_score = get_history_score(guild)

    if user.id in daily_report:
        await leetcode_channel.send(user.mention + " you have already joined the leetcode daily coding challenge!")
    else:
        await user.add_roles(leetcode_role)

        daily_report[user.id] = 0
        update_daily_report(guild, daily_report)

        history_score[user.id] = 0
        update_history_score(guild, history_score)

        await leetcode_channel.send(user.mention + " you successfully join the leetcode daily coding challenge!")
    
async def quit(user: discord.Member, guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    leetcode_role = get_leetcode_role(guild)

    synchronize_daily_report_member(guild)
    daily_report = get_daily_report(guild)

    synchronize_history_score(guild)
    history_score = get_history_score(guild)

    if user.id in daily_report:
        await user.remove_roles(leetcode_role)

        del daily_report[user.id]
        update_daily_report(guild, daily_report)
        
        del history_score[user.id]
        update_history_score(guild, history_score)

        await leetcode_channel.send(user.mention + " you successfully quit the leetcode daily coding challenge!")
    else:
        await leetcode_channel.send(user.mention + " you have not joined the leetcode daily coding challenge!")

# $leetcode list
async def show_leetcode_participants(guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    leetcode_role = get_leetcode_role(guild)
    message = "Current participants"
    
    names = ""
    for index, member in enumerate(leetcode_role.members):
        names += f"\n{index + 1}. {member.name}"
    message += f" (total participants: {len(leetcode_role.members)}):{names}"
    
    await leetcode_channel.send(message)

# $leetcode leaderboard
async def show_leaderboard(guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    history_score = get_history_score(guild)
    rank = list(history_score.items())
    rank.sort(key=lambda x: x[1], reverse=True)
    
    message = "Leaderboard"
    names = ""
    for index, (user_id, value) in enumerate(rank):
        user = guild.get_member(user_id)
        names += f"\n{index + 1}. {user.name} ({value})"
    message += f" (total participants: {len(rank)}):{names}"
    await leetcode_channel.send(message)

# $leetcode start
async def add_leetcode_schedule(scheduler, guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    scheduler.add_job(
        leetcode_start,
        CronTrigger(
            hour=start_time['hour'],
            minute=start_time['minute'],
            second=start_time['second'],
            timezone=timezone
        ),
        args=(guild,),
        misfire_grace_time=None,
        id=f"leetcode start {guild.id}"
    )
    scheduler.add_job(
        leetcode_end,
        CronTrigger(
            hour=end_time['hour'],
            minute=end_time['minute'],
            second=end_time['second'],
            timezone=timezone
        ),
        args=(guild,),
        misfire_grace_time=None,
        id=f"leetcode end {guild.id}"
    )

    await leetcode_channel.send(
        f"Leetcode daily coding challenge job all set.\n" +
        f"Daily start time: {start_time['hour']}:{start_time['minute']}:{start_time['second']}\n" +
        f"Daily end time: {end_time['hour']}:{end_time['minute']}:{end_time['second']}"
    )

# $leetcode stop
async def remove_leetcode_schedule(scheduler, guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    if scheduler.get_job(f"leetcode start {guild.id}"):
        scheduler.remove_job(f"leetcode start {guild.id}")
    if scheduler.get_job(f"leetcode end {guild.id}"):
        scheduler.remove_job(f"leetcode end {guild.id}")
    await leetcode_channel.send("Leetcode daily coding challenge job is removed.")

# $leetcode today
async def show_today_challenge(guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    await leetcode_channel.send(embed=get_daily_coding_challenge())

async def leetcode_start(guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    leetcode_role = get_leetcode_role(guild)
    embed = get_daily_coding_challenge()
    await leetcode_channel.send(embed=embed)
    await leetcode_channel.send(f"The new daily coding challenge has released! {leetcode_role.mention}")

async def leetcode_end(guild: discord.Guild):
    leetcode_channel = get_leetcode_channel(guild)
    daily_report = get_daily_report(guild)
    completedUser = ""
    completedCount = 0
    unfinishedUser = ""
    unfinishedCount = 0
    for user_id, value in daily_report.items():
        user = guild.get_member(user_id)
        if value == 1:
            completedCount += 1
            completedUser += f"\n{completedCount}. {user.name}"
            daily_report[user_id] = 0
        else:
            unfinishedCount += 1
            unfinishedUser += f"\n{unfinishedCount}. {user.name}"
    content = "Today's leetcode daily coding challenge has ended."
    if completedCount > 0:
        content += f"\nCompleted participants (total: {completedCount}):" + completedUser
    if unfinishedCount > 0:
        content += f"\nUnfinished participants (total: {unfinishedCount}):" + unfinishedUser
    await leetcode_channel.send(content)

    update_daily_report(guild, daily_report)

def get_daily_coding_challenge():
    leetcode_url = "https://leetcode.com"
    post_url = leetcode_url + "/graphql"
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
    questionDate = result['date']
    questionID = result['question']['questionId']
    title = result['question']['title']
    questionLink = leetcode_url + result['link']
    acRate = result['question']['acRate']
    difficulty = result['question']['difficulty']
    likes = result['question']['likes']
    dislikes = result['question']['dislikes']
    content = result['question']['content']
    paidOnly = result['question']['paidOnly']
    hasSolution = result['question']['hasSolution']
    topicTags = result['question']['topicTags']
    similarQuestions = json.loads(result['question']['similarQuestions'])

    embed = discord.Embed()

    embed.title = f"🏆 Leetcode Daily Coding Challenge ({questionDate})"

    # problem field
    problemField = {}
    if paidOnly:
        problemField['name'] = f"Problem {questionID} 💰"
    else:
        problemField['name'] = f"Problem {questionID}"
    problemField['value'] = f"[{title}]({questionLink}) ({difficulty})"
    if hasSolution:
        problemField['value'] += f" [Solution]({questionLink})"
    problemField['inline'] = False
    embed.add_field(name=problemField['name'], value=problemField['value'], inline=problemField['inline'])

    # acceptance rate field
    acceptanceField = {'name': f"Acceptance", 'value': f"{round(acRate, 2)}%", 'inline': True}
    embed.add_field(name=acceptanceField['name'], value=acceptanceField['value'], inline=acceptanceField['inline'])

    # like field
    likeField = {'name': f"👍 Like", 'value': likes, 'inline': True}
    embed.add_field(name=likeField['name'], value=likeField['value'], inline=likeField['inline'])

    # dislike field
    dislikeField = {'name': f"👎 Dislike", 'value': dislikes, 'inline': True}
    embed.add_field(name=dislikeField['name'], value=dislikeField['value'], inline=dislikeField['inline'])

    # related topic field
    topicFieldValue = ""
    for i in range(len(topicTags)):
        topicFieldValue += f"[{topicTags[i]['name']}]({leetcode_url}/tag/{topicTags[i]['slug']}/)"
        if i != len(topicTags) - 1:
            topicFieldValue += ', '
    embed.add_field(name="Related topics", value=topicFieldValue, inline=False)

    # similar questions field
    similarFieldValue = ""
    for i in range(len(similarQuestions)):
        similarFieldValue += f"[{similarQuestions[i]['title']}]({leetcode_url}/problems/{similarQuestions[i]['titleSlug']}/) ({similarQuestions[i]['difficulty']})"
        if i != len(similarQuestions) - 1:
            similarFieldValue += ', '
    if len(similarQuestions) > 0:
        embed.add_field(name='Similar questions', value=similarFieldValue, inline=False)

    return embed
