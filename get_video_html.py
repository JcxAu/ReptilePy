from bs4 import BeautifulSoup
import log, language, change_ini
import requests, os, time

ua: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}
language_d: dict = language.SimplifiedChinese_SimplifiedChinese
log_file_name: str = change_ini.log_file_name
video_num = 0


def get_data(url: str, headers: dict, ssl: bool = True) -> dict:
    res_d = {'state': None, 'info': None, 'text': None}
    try:
        result = requests.get(url, headers=headers, timeout=(4, 4), verify=ssl)
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language_d['请求超时 !']
        return res_d
    if result.status_code == 200:
        result.encoding = result.apparent_encoding
        res_d['state'] = '成功'
        res_d['text'] = result.text
        return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = language_d['视频请求失败 !'] + language_d['状态码为: '] + str(result.status_code)
        return res_d


# 获得所有的指定标签


def get_tag(html: str, tags: list, parser: str = 'html.parser') -> dict:
    res_d = {'state': None, 'info': None, 'tag_list': None}
    tags_l = []
    try:
        soup = BeautifulSoup(html, parser)
        for tag in tags:
            tags_l = tags_l + soup.select(tag)
        if not tags_l:
            res_d['state'] = '失败'
            res_d['info'] = language_d['没有发现视频的网址 !']
            return res_d

        res_d['state'] = '成功'
        res_d['tag_list'] = tags_l
        return res_d
    except Exception:
        res_d['state'] = '失败'
        res_d['info'] = language_d['视频数据处理出错 !']
        return res_d

# 找到此次开始时的图片序列


def find_video_num():
    global video_num
    video_num_l = []
    res = os.path.exists('./videos')  # 查看文件夹是否存在
    if res is not True:
        os.mkdir('./videos')  # 创建文件夹
        video_num = 0
    else:
        list_dir = os.listdir('./videos')  # 查看 "videos" 文件夹是否有内容
        if list_dir:
            for i in list_dir:  # 循环获取文件夹中每一个文件的名称
                res = i[5:]  # 获取除开头五个文字 (video) 以外的文件名
                key = res.find('.')  # 找到 "." 所在的索引
                video_num_l.append(int(res[:key]))  # 将 "." 以前的内容为 str 类型的数字转换成 int 类型并加入到图片序列中
            video_num = max(video_num_l) + 1  # 获取最大的图片序列并加一, 得到此次开始时的图片序列
        else:
            video_num = 0


def download_video(url: str, headers: dict, ssl: bool = True):
    res_d = {'state': None, 'info': None}
    try:
        data = requests.get(url, headers=headers, timeout=(4, 4), verify=ssl)
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language_d['请求超时 !']
        return res_d
    state = data.status_code
    if state == 200:
        video_bytes = data.content
        suffix_l = url.split('.')
        file = open(f'./videos/video{video_num}.{suffix_l[-1]}', 'wb')
        file.write(video_bytes)
        file.close()

        res_d['state'] = '成功'
        return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = language_d['视频请求失败 !'] + language_d['状态码为: '] + str(state)
        return res_d


def reptile_algorithm(url: str, headers: dict, ssl: bool = True) -> dict:
    global video_num
    flag: bool = True
    videos_l = []
    res_d: dict = {'state': None, 'flag': None}

    if url != '' and ('http://' in url[:7] or 'https://' in url[:8]):
        result = get_data(url, headers, ssl)
        if result['state'] == '成功':
            tag_res_d = get_tag(result['text'], ['video', 'source'])
            if tag_res_d['state'] == '成功':
                for tag in tag_res_d['tag_list']:
                    if tag.get('src') not in videos_l:
                        videos_l.append(tag.get('src'))
                for video_url in videos_l:
                    if '?' in video_url:
                        video_url = video_url.split('?')[0]
                    download_res = download_video(video_url, headers, ssl)
                    if download_res['state'] == '成功':
                        video_num += 1
                    elif download_res['state'] == '失败':
                        flag = False
                        log.write_log(language_d['result: 下载失败, 状态为: '] + str(download_res['info']) + '\nurl: ' + str(url), file_name=log_file_name)
                res_d['flag'] = flag
                return res_d
            else:
                res_d['state'] = '失败'
                log.write_log(language_d['result: 下载失败, 状态为: '] + str(tag_res_d['info']) + '\nurl: ' + str(url), file_name=log_file_name)
                return res_d
        else:
            res_d['state'] = '失败'
            log.write_log(language_d['result: 下载失败, 状态为: '] + str(result['info']) + '\nurl: ' + str(url), file_name=log_file_name)
            return res_d
    else:
        res_d['state'] = '失败'
        log.write_log(language_d['result: 请输入正确的URL !'] + '\nurl: ' + str(url), file_name=log_file_name)
        return res_d


def get_video_html(url: str, num_download: int, lock, time_sleep: float = 0.2, ssl: bool = True) -> dict:
    res_d: dict = {'success': 0, 'error': 0}
    error: int = 0
    success: int = 0
    i = 0
    while i < int(num_download):
        find_video_num()
        lock.acquire()
        result = reptile_algorithm(url, ua, ssl=ssl)
        lock.release()
        if result['state'] == '失败' or result['flag'] is False:
            error += 1
        else:
            success += 1
        i += 1
        time.sleep(time_sleep)
    res_d['success'] = success
    res_d['error'] = error

    return res_d


change_ini.start()
res = change_ini.ask_value('language')
if res != 'None':
    if res == 'English':
        language_d = language.SimplifiedChinese_English
