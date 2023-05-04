#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    discord_utils.py
@Time      :    2023/03/21
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

from typing import Callable, TypeVar

from discord.ext import commands

from lib.Exceptions import UserNotOwner

T = TypeVar("T")

def is_owner(owners: list) -> Callable[[T], T]:
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id not in owners:
            raise UserNotOwner
        return True
    return commands.check(predicate)
