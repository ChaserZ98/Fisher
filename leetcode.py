from apscheduler.triggers.cron import CronTrigger
import requests
import discord
import json

leetcodeParticipantID = {}

def getDailyCodingChallenge():
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

async def addLeetcodeSchedule(scheduler, bot, channel):
    timezone="America/New_York"
    start_time = {
        'hour': "7",
        'minute': "9",
        'second': "50"
    }
    end_time = {
        'hour': "23",
        'minute': "59",
        'second': "59"
    }

    scheduler.add_job(
        leetcode_start,
        CronTrigger(
            hour=start_time['hour'],
            minute=start_time['minute'],
            second=start_time['second'],
            timezone=timezone
        ),
        args=(bot, channel)
    )
    scheduler.add_job(
        leetcode_end,
        CronTrigger(
            hour=end_time['hour'],
            minute=end_time['minute'],
            second=end_time['second'],
            timezone=timezone
        ),
        args=(bot, channel)
    )

async def showLeetcodeParticipants(bot, leetcodeParticipantID, channel):
    validNum = 0
    message = f"Current participants"
    names = ""
    for id in leetcodeParticipantID:
        user = await bot.fetch_user(id)
        if user:
            validNum += 1
            names += f"\n{validNum}. {user.name}"
    message += f" (total participants: {validNum}):{names}"
    
    await channel.send(message)

async def leetcode_start(bot, channel):
    await bot.wait_until_ready()

    embed = getDailyCodingChallenge()
    await channel.send(embed=embed)

    message = "The new daily coding challenge has released!"
    for id in leetcodeParticipantID:
        user = await bot.fetch_user(id)
        if user:
            message += user.mention
    await channel.send(message)

async def leetcode_end(bot, testChannelID):
    await bot.wait_until_ready()
    mainChannel = bot.get_channel(testChannelID)
    await mainChannel.send("func")