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
