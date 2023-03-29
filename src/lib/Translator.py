#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File      :    Translator.py
@Time      :    2023/03/29
@Author    :    Feiyu Zheng
@Version   :    1.0
@Contact   :    feiyuzheng98@gmail.com
@License   :    Copyright (c) 2023-present Feiyu Zheng. All rights reserved.
                This work is licensed under the terms of the MIT license.
                For a copy, see <https://opensource.org/licenses/MIT>.
@Desc      :    None
'''


from typing import Optional

from discord import Locale
from discord.app_commands import Translator, locale_str, TranslationContext, TranslationContextLocation, TranslationError

class FisherTranslator(Translator):
    def __init__(self) -> None:
        super().__init__()
        self.localized_group_name = {}
        self.localized_group_desc = {}
        self.localized_command_name = {}
        self.localized_command_desc = {}
        self.localized_param_name = {}
        self.localized_param_desc = {}
        self.localized_choice_name = {}
        self.localized_other = {}
    
    def update_corpus(self, location: TranslationContextLocation, corpus: dict):
        if location is TranslationContextLocation.group_name:
            self.localized_group_name.update(corpus)
        elif location is TranslationContextLocation.group_description:
            self.localized_group_desc.update(corpus)
        elif location is TranslationContextLocation.command_name:
            self.localized_command_name.update(corpus)
        elif location is TranslationContextLocation.command_description:
            self.localized_command_desc.update(corpus)
        elif location is TranslationContextLocation.parameter_name:
            self.localized_param_name.update(corpus)
        elif location is TranslationContextLocation.parameter_description:
            self.localized_param_desc.update(corpus)
        elif location is TranslationContextLocation.choice_name:
            self.localized_choice_name.update(corpus)
        elif location is TranslationContextLocation.other:
            self.localized_other.update(corpus)
        else:
            raise TypeError(f"Invalid TranslationContextLocation type: {location}")
        
    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext) -> Optional[str]:
        if context.location is TranslationContextLocation.group_name:
            if locale in self.localized_group_name[string.message]:
                return self.localized_group_name[string.message][locale]
        elif context.location is TranslationContextLocation.command_name:
            if locale in self.localized_command_name[string.message]:
                return self.localized_command_name[string.message][locale]
        
        return None
        
            
        raise TranslationError(string=string, locale=locale, context=context)