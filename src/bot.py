#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    bot.py
@Time      :    2023/03/27
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

import asyncio
import json
import os
import sys
import time

import discord
from dotenv import load_dotenv
import uvloop

from lib.Fisher import Fisher
from utils.log import init_logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

src_dir = os.path.realpath(os.path.dirname(__file__))
home_dir = os.path.realpath(os.path.join(src_dir, '..'))
log_dir = os.path.join(home_dir, 'log')
config_dir = os.path.join(home_dir, 'config')
data_dir = os.path.join(home_dir, 'data')

logger = init_logger(logger_name='Fisher', log_dir=log_dir)
logger.info("Logger loaded")

load_dotenv()
if os.getenv('BOT_TOKEN') is None:
    logger.error('BOT_TOKEN is not defined in ENV')
    sys.exit()
if os.getenv('BOT_ENV') is None:
    logger.error('BOT_ENV is not defined in ENV')
    sys.exit()
logger.info('ENV variables loaded')

if os.path.exists(os.path.join(config_dir, 'config.json')):
    with open(os.path.join(config_dir, 'config.json'), 'r') as file:
        config = json.load(file)[os.getenv('BOT_ENV')]
    logger.info("Config file loaded")
else:
    logger.error("'config/config.json' is not found! Please add it and try again")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
logger.info("Bot intents loaded")

try:
    bot = Fisher(
        intents=intents,
        logger=logger,
        config=config,
        bot_status=config['bot_status'],
        data_dir=data_dir,
    )
except Exception as e:
    logger.error(f"Bot instatiation failed: {e}")
    sys.exit(1)
logger.info("Bot instatiation complete")

try:
    bot.start_time = time.perf_counter()
    bot.run(os.getenv("BOT_TOKEN"))
except Exception as e:
    bot.logger.exception(f'Bot log in failed: {e}')

bot.logger.info("Bot exited")