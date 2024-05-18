import io, requests, os, time
from PIL import Image
from bs4 import BeautifulSoup
import log, language, change_ini

ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}
src = []
pic_num = 0
pic_num_list = []
language_d = language.SimplifiedChinese_SimplifiedChinese

# 获得指定 url 的网页


def get_data(url: str, ua: dict, ssl: bool = True) -> dict:
    res_d = {'state': None, 'info': None, 'text': None}
    try:
        result = requests.get(url, headers=ua, timeout=(4, 4), verify=ssl)
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language_d['请求超时 !']
        return res_d
    if result.status_code == 200:
        result.encoding = 'utf-8'
        res_d['state'] = '成功'
        res_d['text'] = result.text
        return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = language_d['图片请求失败 !'] + language_d['状态码为: '] + str(result.status_code)
        return res_d

# 获得所有的指定标签


def get_tag(html: str, tag: str, parser: str = 'html.parser') -> dict:
    res_d = {'state': None, 'info': None, 'tag_list': None}
    try:
        soup = BeautifulSoup(html, parser)
        tag_list = soup.select(tag)
        res_d['state'] = '成功'
        res_d['tag_list'] = tag_list
        return res_d
    except Exception:
        res_d['state'] = '失败'
        res_d['info'] = language_d['图片数据处理出错 !']
        return res_d

# 下载图片


def download_img(url: str, ua: dict, ssl: bool = True) -> dict:
    res_d = {'state': None, 'info': None}
    try:
        data = requests.get(url, headers=ua, timeout=(4, 6), verify=ssl)
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language_d['请求超时 !']
        return res_d
    download_state = data.status_code
    if download_state == 200:
        try:
            data_img = data.content
            bytes_img = io.BytesIO(data_img)
            im = Image.open(bytes_img)
            o = open('./photos/img' + str(pic_num) + '.' + im.format, 'wb')
            o.write(data_img)
            o.close()

            res_d['state'] = '成功'
            return res_d
        except Exception:
            res_d['state'] = '失败'
            res_d['info'] = language_d['图片数据处理出错 !']
            return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = language_d['图片请求失败 !'] + language_d['状态码为: '] + str(download_state)
        return res_d

# 找到此次开始时的图片序列


def find_pic_num():
    global pic_num
    pic_num_l = []
    res = os.path.exists('./photos')  # 查看文件夹是否存在
    if res is not True:
        os.mkdir('./photos')  # 创建文件夹
        pic_num = 0
    else:
        list_dir = os.listdir('./photos')  # 查看 "photos" 文件夹是否有内容
        if list_dir:
            for i in list_dir:  # 循环获取文件夹中每一个文件的名称
                res = i[3:]  # 获取除开头三个文字 (img) 以外的文件名
                key = res.find('.')  # 找到 "." 所在的索引
                pic_num_l.append(int(res[:key]))  # 将 "." 以前的内容为 str 类型的数字转换成 int 类型并加入到图片序列中
            pic_num = max(pic_num_l) + 1  # 获取最大的图片序列并加一, 得到此次开始时的图片序列
        else:
            pic_num = 0

# 找到图片的 url


def find_url_algorithm(url: str, ua: dict, ssl: bool = True) -> dict:
    res_d: dict = {'state': None, 'url_l': None}
    url_l: list = []
    data_res_d = get_data(url, ua, ssl)
    if data_res_d['state'] != '失败':
        tags_res_d = get_tag(data_res_d['text'], 'img')
        if tags_res_d['state'] == '成功':
            for tag in tags_res_d['tag_list']:
                old_tag = tag
                url = tag.get('src')
                if url is not None:
                    if 'https://' == url[:8]:
                        url_l.append(url)
                    elif 'http://' == url[:7]:
                        url_l.append(url)
                    elif '//' == url[:2]:
                        new_url = 'http:' + url
                        url_l.append(new_url)
                    elif '/' == url[:1]:
                        new_url = 'http:/' + url
                        url_l.append(new_url)
                    else:
                        new_url = 'http://' + url
                        url_l.append(new_url)
                else:
                    url = old_tag.get('data-src')
                    if url is not None:
                        if 'https://' == url[:8]:
                            url_l.append(url)
                        elif 'http://' == url[:7]:
                            url_l.append(url)
                        elif '//' == url[:2]:
                            new_url = 'http:' + url
                            url_l.append(new_url)
                        elif '/' == url[:1]:
                            new_url = 'http:/' + url
                            url_l.append(new_url)
                        else:
                            new_url = 'http://' + url
                            url_l.append(new_url)
            if url_l:
                res_d['state'] = '成功'
                res_d['url_l'] = url_l
                return res_d
            else:
                res_d['state'] = '失败'
                log.write_log(language_d['result: 下载失败, 状态为: '] + language_d['没有发现图片的网址 !'] + '\nurl: ' + str(url))
                return res_d
        else:
            res_d['state'] = '失败'
            log.write_log(language_d['result: 下载失败, 状态为: '] + str(tags_res_d['info']) + '\nurl: ' + str(url))
            return res_d
    else:
        res_d['state'] = '失败'
        log.write_log(language_d['result: 下载失败, 状态为: '] + str(data_res_d['info']) + '\nurl: ' + str(url))
        return res_d

# 爬取图片的主函数


def reptile_algorithm(url: str, ua: dict, ssl: bool = True) -> dict:
    global pic_num
    res_d = {'state': None, 'flag': None}
    flag: bool = True

    if url != '' and ('http://' in url[:7] or 'https://' in url[:8]):
        result = find_url_algorithm(url, ua, ssl)
        if result['state'] == '成功':
            for img_url in result['url_l']:
                download_res = download_img(img_url, ua, ssl)
                if download_res['state'] == '成功':
                    pic_num += 1
                elif download_res['state'] == '失败':
                    flag = False
                    log.write_log(language_d['result: 下载失败, 状态为: '] + str(download_res['info']) + '\nurl: ' + str(url))
            res_d['flag'] = flag
            return res_d
        else:
            res_d['state'] = '失败'
            return res_d
    else:
        res_d['state'] = '失败'
        log.write_log(language_d['result: 请输入正确的URL !'] + '\nurl: ' + str(url))
        return res_d

# 集成函数 (只要用这个就好了)


def get_date_html(url: str, num_download: int, lock, time_sleep: float = 0.2, ssl: bool = True) -> dict:
    res_d: dict = {'success': 0, 'error': 0}
    error: int = 0
    success: int = 0
    i = 0
    while i < int(num_download):
        find_pic_num()
        lock.acquire()
        reptile_res_d = reptile_algorithm(url, ua, ssl=ssl)
        lock.release()
        if reptile_res_d['state'] == '失败' or reptile_res_d['flag'] is False:
            error += 1
        else:
            success += 1
        i += 1
        time.sleep(time_sleep)

    res_d['success'] = success
    res_d['error'] = error

    if int(num_download) != 0:
        return res_d
    else:
        return res_d


change_ini.start()
res = change_ini.ask_value('language')
if res != change_ini.language_d['暂无']:
    if res == 'English':
        language_d = language.SimplifiedChinese_English
