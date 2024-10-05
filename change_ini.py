# Copyright (c) 2024, JcxAu
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# See the LICENSE file for more details.
import configparser
import os.path, time
import language

language_d = language.SimplifiedChinese_SimplifiedChinese
log_file_name = time.ctime().replace(':', '：') + '.log'
sections = []


# 询问选项的值


def ask_value(key: str):
    if "setting" in sections:
        if key in conf.options('setting'):
            value = conf.get('setting', key)
            return value
        else:
            return 'None'
    else:
        return 'None'

# 检查 ini 文件


def inspect_ini():
    global sections

    result = os.path.exists('./config.ini')
    if result:
        conf.read('./config.ini')
    else:
        file = open('./config.ini', 'a', encoding='utf-8')
        file.close()

    sections = conf.sections()

# 改变下载数量


def change_download_num(num):
    if 'setting' in sections:
        conf.set('setting', 'download_num', str(num))
    else:
        conf.add_section('setting')
        sections.append('setting')
        change_download_num(num)

# 改变 ssl开启状态


def change_ssl_open_state(ssl_state: bool = True):
    if 'setting' in sections:
        conf.set('setting', 'ssl_open_state', str(ssl_state))
    else:
        conf.add_section('setting')
        sections.append('setting')
        change_ssl_open_state(ssl_state)

# 改变下载模式


def change_download_mode(mode: str):
    if "setting" in sections:
        conf.set('setting', 'download_mode', str(mode))
    else:
        conf.add_section('setting')
        sections.append('setting')
        change_download_mode(mode)

# 改变语言


def change_language(program_language: str):
    if 'setting' in sections:
        conf.set('setting', 'language', str(program_language))
    else:
        conf.add_section('setting')
        sections.append('setting')
        change_language(program_language)


# 保存设置


def save_set_up():
    file = open('./config.ini', 'w', encoding='utf-8')
    conf.write(file)
    file.close()

# 初始化 (一开始用它就对了)


def start():
    global conf
    conf = configparser.ConfigParser()
    inspect_ini()


start()
res = ask_value('language')
if res != '暂无':
    if res == 'English':
        language = language.SimplifiedChinese_English
