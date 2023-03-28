#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    log.py
@Time      :    2023/03/27 19:19:13
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023 Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''

import logging
from logging.handlers import RotatingFileHandler
import os

class ColorFormatter(logging.Formatter):
    # Font Colors
    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    GRAY = "\x1b[38m"
    
    # Font Styles
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"

    COLORS = {
        logging.DEBUG: GRAY + BOLD,
        logging.INFO: BLUE + BOLD,
        logging.WARNING: YELLOW + BOLD,
        logging.ERROR: RED,
        logging.CRITICAL: RED + BOLD,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.BLACK + self.BOLD)
        format = format.replace("(reset)", self.RESET)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.GREEN + self.BOLD)
        
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")

        return formatter.format(record)

def init_logger(logger_name: str, log_dir: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

    # file handlers
    file_handler_formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")

    debug_file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'debug.log'),
        maxBytes=1024 * 1024 * 2,
        backupCount=5,
        encoding='utf-8'
    )
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(file_handler_formatter)
    logger.addHandler(debug_file_handler)

    info_file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'info.log'),
        maxBytes=1024 * 1024 * 1,
        backupCount=5,
        encoding='utf-8'
    )
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(file_handler_formatter)
    logger.addHandler(info_file_handler)

    error_file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        maxBytes=1024 * 1024 * 1,
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_handler_formatter)
    logger.addHandler(error_file_handler)

    return logger
