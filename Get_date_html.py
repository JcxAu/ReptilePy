import io, requests, os, time
from PIL import Image
from bs4 import BeautifulSoup
import Log, Language, Change_ini

ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}
src = []
pic_num = 0
pic_num_list = []
state = 'Error'
language = Language.SimplifiedChinese_SimplifiedChinese

# 获得指定 url 的网页


def get_data(url: str, ua: dict, ssl: bool = True):
    global state
    try:
        r = requests.get(url, headers=ua, timeout=(4, 4), verify=ssl)
    except requests.exceptions.RequestException:
        state = language['请求超时 !']
        return '下载失败'
    if r.status_code == 200:
        r.encoding = 'utf-8'
        return r.text
    else:
        state = language['图片请求失败 !'] + language['状态码为: '] + str(r.status_code)
        return '下载失败'

# 获得所有的指定标签


def get_tag(html: str, tag: str, parser: str = 'html.parser'):
    global state
    try:
        soup = BeautifulSoup(html, parser)
        tag_list = soup.select(tag)
        return tag_list
    except Exception:
        state = language['图片数据处理出错 !']
        return '下载失败'


# 下载图片


def download_img(url: str, ua: dict, ssl: bool = True):
    global state
    try:
        data = requests.get(url, headers=ua, timeout=(4, 6), verify=ssl)
    except requests.exceptions.RequestException:
        state = language['请求超时 !']
        return '下载失败'
    state = data.status_code
    if state == 200:
        try:
            data_img = data.content
            bytes_img = io.BytesIO(data_img)
            im = Image.open(bytes_img)
            o = open('./photos/img' + str(pic_num) + '.' + im.format, 'wb')
            o.write(data_img)
            o.close()

        except Exception:
            state = language['图片数据处理出错 !']
            return '下载失败'
    else:
        state = language['图片请求失败 !'] + language['状态码为: '] + str(state)
        return '下载失败'

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


def find_url_algorithm(url: str, ua: dict, ssl: bool = True):
    url_l = []
    html_data = get_data(url, ua, ssl)
    if html_data != '下载失败':
        tags = get_tag(html_data, 'img')
        if tags != '下载失败':
            for tag in tags:
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
                return url_l
            else:
                Log.write_log(language['result: 下载失败, 状态为: '] + language['没有发现图片的网址 !'] + '\nurl: ' + str(url))
                return '下载失败'
        else:
            Log.write_log(language['result: 下载失败, 状态为: '] + str(state) + '\nurl: ' + str(url))
            return '下载失败'
    else:
        Log.write_log(language['result: 下载失败, 状态为: '] + str(state) + '\nurl: ' + str(url))
        return '下载失败'

# 爬取图片的主函数


def reptile_algorithm(url: str, ua: dict, lock, ssl: bool = True):
    global pic_num
    flag: bool = True

    if url != '' and 'http' == url[:4]:
        lock.acquire()
        result = find_url_algorithm(url, ua, ssl)
        lock.release()
        if result != '下载失败':
            for img_url in result:
                lock.acquire()
                info = download_img(img_url, ua, ssl)
                if info != '下载失败':
                    pic_num += 1
                elif info == '下载失败':
                    flag = False
                    Log.write_log(language['result: 下载失败, 状态为: '] + str(state) + '\nurl: ' + str(url))
                lock.release()

            return flag
        else:
            return '下载失败'
    else:
        Log.write_log(language['result: 请输入正确的URL !'] + '\nurl: ' + str(url))
        return '下载失败'


# 集成函数 (只要用这个就好了)


def get_date_html(url: str, num_download: int, lock, time_sleep: float = 0.2, ssl: bool = True) -> int:
    download_error: int = 0
    i = 0
    while i < int(num_download):
        find_pic_num()
        reptile_res = reptile_algorithm(url, ua, lock, ssl=ssl)
        if reptile_res == '下载失败' or reptile_res is False:
            download_error += 1
        i += 1
        time.sleep(time_sleep)

    if int(num_download) != 0:
        return download_error
    else:
        return 0


Change_ini.start()
res = Change_ini.ask_value('language')
if res != Change_ini.language['暂无']:
    if res == 'English':
        language = Language.SimplifiedChinese_English
