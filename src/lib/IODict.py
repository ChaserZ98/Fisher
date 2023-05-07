#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    IODict.py
@Time      :    2023/03/29
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

from enum import Enum

from utils.io_utils import dump_data

class SerializationType(Enum):
    JSON = 'json'
    PKL = 'pkl'

class IODict(dict):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    @property
    def file_path(self):
        return self._file_path
    
    @file_path.setter
    def path(self, val):
        self._file_path = val

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)
        dump_data(data=self, file_path=self.file_path)
    
    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        dump_data(data=self, file_path=self.file_path)
