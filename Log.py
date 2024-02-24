import time
import os.path

# 准备文件


def start():
    res = os.path.exists('./download_info.log')
    if not res:
        file = open('./download_info.log', 'a', encoding='utf-8')
        file.close()

# 写入日志


def write_log(value: str):
    start()
    file = open('./download_info.log', 'a', encoding='utf-8')
    file.write('time: ' + str(time.ctime()) + ': \n' + value + '\n\n')
    file.close()
