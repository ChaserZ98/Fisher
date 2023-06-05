#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    LeetcodeGuild.py
@Time      :    2023/06/03
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

import os
from typing import Union, Type

from lib.IODict import IODict
from utils.io_utils import load_data

class LeetcodeGuild:
    __slots__ = ('_config', '_daily_report', '_history_score')

    def __init__(
        self,
        guild_module_data_dir_path: str,
        leetcode_role_id: int,
        leetcode_channel_id: int,
        config_file_name: str = 'config.json',
        sync: bool = True
    ):
        """_summary_

        Args:
            config (GuildConfigDict): _description_
            daily_report (GuildDailyReportDict): _description_
            history_score (GuildHistoryScoreDict): _description_
        """

        config_file_path = os.path.join(guild_module_data_dir_path, config_file_name)
        self.config = GuildConfigDict(config_file_path, leetcode_role_id, leetcode_channel_id, daily_challenge_status=True, sync=sync)

        daily_report_file_path = os.path.join(guild_module_data_dir_path, self.config['daily_report_file_name'])
        self.daily_report = GuildDailyReportDict(daily_report_file_path, sync=sync)

        history_score_file_path = os.path.join(guild_module_data_dir_path, self.config['history_score_file_name'])
        self.history_score = GuildHistoryScoreDict(history_score_file_path, sync=sync)
    
    @classmethod
    def from_file(
        cls: Type['LeetcodeGuild'],
        guild_module_data_dir_path: str,
        config_file_name: str = 'config.json'
    ) -> 'LeetcodeGuild':
        """_summary_

        Args:
            cls (Type[&#39;LeetcodeGuild&#39;]): _description_
            guild_module_data_dir_path (str): _description_
            config_file_name (str, optional): _description_. Defaults to 'config.json'.

        Returns:
            LeetcodeGuild: _description_
        """
        
        config_file_path = os.path.join(guild_module_data_dir_path, config_file_name)
        config = GuildConfigDict.from_file(config_file_path)
        
        daily_report_file_path = os.path.join(guild_module_data_dir_path, config['daily_report_file_name'])
        daily_report = GuildDailyReportDict.from_file(daily_report_file_path)

        history_score_file_path = os.path.join(guild_module_data_dir_path, config['history_score_file_name'])
        history_score = GuildHistoryScoreDict.from_file(history_score_file_path)

        leetcodeGuild = cls(guild_module_data_dir_path, config['leetcode_role_id'], config['leetcode_channel_id'], config_file_name, sync=False)
        leetcodeGuild.config = config
        leetcodeGuild.daily_report = daily_report
        leetcodeGuild.history_score = history_score
        
        return leetcodeGuild
        
    
    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, val: 'GuildConfigDict'):
        self._config = val
    
    @property
    def daily_report(self):
        return self._daily_report
    
    @daily_report.setter
    def daily_report(self, val: 'GuildDailyReportDict'):
        self._daily_report = val
    
    @property
    def history_score(self):
        return self._history_score
    
    @history_score.setter
    def history_score(self, val: 'GuildHistoryScoreDict'):
        self._history_score = val


class GuildConfigDict(IODict):
    def __init__(
        self,
        file_path: str,
        leetcode_role_id: int,
        leetcode_channel_id: int,
        daily_challenge_status: bool = False,
        timezone: str = 'UTC',
        start_time: dict = {'hour': "00", 'minute': "00", 'second': "00"},
        end_time: dict = {'hour': "23", 'minute': "59", 'second': "59"},
        remind_time: dict = {'hour': "23", 'minute': "00", 'second': "00"},
        daily_report_file_name: str = "daily report.json",
        history_score_file_name: str = "history score.json",
        sync: bool = True
    ):
        """An IODict subclass for guild config

        Args:
            file_path (str): config file path
            leetcode_role_id (int): leetcode role id
            leetcode_channel_id (int): leetcode channel id
            daily_challenge_status (bool, optional): daily challenge status. Defaults to False.
            timezone (str, optional): timezone used for daily challenge. Defaults to 'UTC'.
            start_time (dict, optional): daily challenge start time. Defaults to {'hour': "00", 'minute': "00", 'second': "00"}.
            end_time (dict, optional): daily challenge end time. Defaults to {'hour': "23", 'minute': "59", 'second': "59"}.
            remind_time (dict, optional): daily challenge remind time. Defaults to {'hour': "23", 'minute': "00", 'second': "00"}.
            daily_report_file_name (str, optional): daily report file name. Defaults to "daily report".
            history_score_file_name (str, optional): history score file name. Defaults to "history score".
            sync (bool, optional): whether sync to the file. Defaults to True.
        """
        dict.__setitem__(self, 'leetcode_role_id', int(leetcode_role_id))
        dict.__setitem__(self, 'leetcode_channel_id', int(leetcode_channel_id))
        dict.__setitem__(self, 'daily_challenge_status', daily_challenge_status)
        dict.__setitem__(self, 'timezone', timezone)
        dict.__setitem__(self, 'start_time', start_time)
        dict.__setitem__(self, 'end_time', end_time)
        dict.__setitem__(self, 'remind_time', remind_time)
        dict.__setitem__(self, 'daily_report_file_name', daily_report_file_name)
        dict.__setitem__(self, 'history_score_file_name', history_score_file_name)
        super().__init__(file_path, sync)
    
    @classmethod
    def from_file(
        cls: Type['GuildConfigDict'],
        file_path: str
    ) -> 'GuildConfigDict':
        """static method to create a GuildConfigDict instance from file

        Args:
            cls (Type['GuildConfigDict']): GuildConfigDict constructor
            file_path (str): config file path

        Returns:
            GuildConfigDict: GuildConfigDict instance
        """
        return cls(file_path, **load_data(file_path), sync=False)
    
    @property
    def leetcode_role_id(self) -> int:
        return self['leetcode_role_id']
    
    @leetcode_role_id.setter
    def leetcode_role_id(self, val: int):
        assert isinstance(val, int), f"TypeError: leetcode_role_id has to be of type int, received {type(val)}"
        self['leetcode_role_id'] = val
    
    @property
    def leetcode_channel_id(self) -> int:
        return self['leetcode_channel_id']
    
    @leetcode_channel_id.setter
    def leetcode_channel_id(self, val: int):
        assert isinstance(val, int), f"TypeError: leetcode_channel_id has to be of type int, received {type(val)}"
        self['leetcode_channel_id'] = val
    
    @property
    def timezone(self) -> str:
        return self['timezone']
    
    @timezone.setter
    def timezone(self, val: str):
        self['timezone'] = val
    
    @property
    def start_time(self) -> dict:
        return self['start_time']
    
    @start_time.setter
    def start_time(self, val: dict):
        self['start_time'] = val
    
    @property
    def end_time(self) -> dict:
        return self['end_time']
    
    @end_time.setter
    def end_time(self, val: dict):
        self['end_time'] = val
    
    @property
    def remind_time(self) -> dict:
        return self['remind_time']
    
    @remind_time.setter
    def remind_time(self, val: dict):
        self['remind_time'] = val
    
    
    def __setitem__(self, key, value) -> None:
        assert key in self, f"KeyError: Invalid key f{key}"
        super().__setitem__(key, value)

class GuildDailyReportDict(IODict):
    def __init__(
        self,
        file_path: str,
        sync: bool = True
    ):
        """An IODict subclass for guild daily report

        Args:
            file_path (str): daily report file path
            sync (bool, optional): whether sync to the file. Defaults to True.
        """
        super().__init__(file_path, sync)
    
    @classmethod
    def from_file(
        cls: Type['GuildDailyReportDict'],
        file_path: str
    ) -> 'GuildDailyReportDict':
        """static method to create a GuildDailyReportDict instance from file

        Args:
            cls (Type['GuildDailyReportDict']): GuildDailyReportDict constructor
            file_path (str): daily report file path

        Returns:
            GuildDailyReportDict: GuildDailyReportDict instance
        """
        d = cls(file_path, sync=False)
        for k, v in load_data(file_path).items():
            dict.__setitem__(d, int(k), v)
        return d

class GuildHistoryScoreDict(IODict):
    def __init__(
        self,
        file_path: str,
        sync: bool = True
    ):
        """An IODict subclass for guild history score

        Args:
            file_path (str): history score file path
            sync (bool, optional): whether sync to the file. Defaults to True.
        """
        super().__init__(file_path, sync)
    
    @classmethod
    def from_file(
        cls: Type['GuildHistoryScoreDict'],
        file_path: str
    ) -> 'GuildHistoryScoreDict':
        """static method to create a GuildHistoryScoreDict instance from file

        Args:
            cls (Type['GuildHistoryScoreDict']): GuildHistoryScoreDict constructor
            file_path (str): history score file path

        Returns:
            GuildHistoryScoreDict: GuildHistoryScoreDict instance
        """
        d = cls(file_path, sync=False)
        for k, v in load_data(file_path).items():
            dict.__setitem__(d, int(k), v)
        return d
