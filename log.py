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
import time
import os, os.path

# 准备文件


def start(file_name: str):
    res = os.path.exists('./log')
    if not res:
        os.mkdir('./log')
    file = open('./log/' + file_name, 'a', encoding='utf-8')
    file.close()

# 写入日志


def write_log(value: str, file_name: str):
    start(file_name)
    file = open('./log/' + file_name, 'a', encoding='utf-8')
    file.write('time: ' + time.ctime() + ': \n' + value + '\n\n')
    file.close()
