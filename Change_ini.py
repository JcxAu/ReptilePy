import configparser
import os.path
import Language

language = Language.SimplifiedChinese_SimplifiedChinese
sections = []

# 一个操作文本的函数


def operate_text(address: str, mode: str, code: str = 'utf-8', write_value: str = ''):
    if mode == 'read':
        f = open(address, 'r', encoding=code)
        result = f.read()
        f.close()
        return result
    elif mode == 'write':
        f = open(address, 'w', encoding=code)
        f.write(write_value)
        f.close()
    elif mode == 'append':
        f = open(address, 'a', encoding=code)
        f.write(write_value)
        f.close()
    elif mode == 'set_up':
        f = open(address, 'w', encoding=code)
        f.close()
    elif mode == 'write_config':
        f = open(address, 'w', encoding=code)
        return f

# 询问选项的值


def ask_value(key: str):
    if "setting" in sections:
        if key in conf.options('setting'):
            value = conf.get('setting', key)
            return value
        else:
            return language['暂无']
    else:
        return language['暂无']

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
    f = operate_text('./config.ini', 'write_config', code='utf-8')
    conf.write(f)
    f.close()

# 初始化 (一开始用它就对了)


def start():
    global conf
    conf = configparser.ConfigParser()
    inspect_ini()


start()
res = ask_value('language')
if res != '暂无':
    if res == 'English':
        language = Language.SimplifiedChinese_English
