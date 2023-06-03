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

import discord
from discord.ext import commands

from lib.Exceptions import UserNotOwner

T = TypeVar("T")

def is_owner(owners: list) -> Callable[[T], T]:
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id not in owners:
            raise UserNotOwner
        return True
    return commands.check(predicate)

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