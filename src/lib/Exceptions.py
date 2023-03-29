#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    Exceptions.py
@Time      :    2023/03/28 09:25:27
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023 Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

from discord.ext import commands

class UserNotOwner(commands.CheckFailure):
    def __init__(self, messsage="User is not an owner of the bot!"):
        self.message = messsage
        super().__init__(self.message)

class UserBlackListed(commands.CheckFailure):
    def __init__(self, message="User is blacklisted"):
        self.message = message
        super().__init__(self.message)