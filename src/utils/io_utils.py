#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    io_utils.py
@Time      :    2023/03/28
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

import os
import json
import pickle

import traceback

def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
    return wrapper
            
@exception_handler
def load_data(file_path):
    _, ext = os.path.splitext(file_path)
    if ext == '.json':
        return load_json(file_path)
    elif ext == '.pkl':
        return load_pkl(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

@exception_handler
def dump_data(data, file_path):
    _, ext = os.path.splitext(file_path)
    
    if ext == '.json':
        return dump_json(data, file_path)
    elif ext == '.pkl':
        return dump_pkl(data, file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_pkl(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data

def dump_pkl(data, path):
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return data

def dump_json(data, path, indent=4) -> dict:
    with open(path, 'w') as file:
        json.dump(data, file, indent=indent)

