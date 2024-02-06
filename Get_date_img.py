import requests, os, io, time
from PIL import Image
import Log, Language, Change_ini

ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}
state = 'Error'
pic_num = 0
language = Language.Chinese_Chinese


# 下载图片


def download_img(url: str, ua: str, ssl: str = True):
    global state
    try:
        get_data = requests.get(url, headers=ua, timeout=(5, 7), verify=ssl)
    except requests.exceptions.RequestException:
        state = language['图片请求失败 !']
        return '下载失败'
    state = get_data.status_code
    if state == 200:
        try:
            data_img = get_data.content
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
                i = res.find('.')  # 找到 "." 所在的索引
                pic_num_l.append(int(res[:i]))  # 将 "." 以前的内容为 str 类型的数字转换成 int 类型并加入到图片序列中
            pic_num = max(pic_num_l) + 1  # 获取最大的图片序列并加一, 得到此次开始时的图片序列
        else:
            pic_num = 0


# 爬取图片的主函数


def reptile_algorithm(url: str, ua: str, ssl: bool = True):
    global pic_num
    if url != '' and 'http' == url[:4]:
        info = download_img(url, ua, ssl)
        if info != '下载失败':
            pic_num += 1

        else:
            Log.write_log(language['result: 下载失败, 状态为: '] + str(state) + '\nurl: ' + str(url))
            return '下载失败'
    else:
        Log.write_log(language['result: 请输入正确的URL'] + '\nurl: ' + str(url))
        return '下载失败'


# 集成函数 (只要用这个就行了)


def get_date_img(url: str, num_download: int, lock, time_sleep: float = 0.2, ssl: bool = True) -> int:
    download_error = 0
    i = 0
    while i < int(num_download):
        find_pic_num()
        lock.acquire()
        reptile_res = reptile_algorithm(url, ua, ssl=ssl)
        lock.release()
        if reptile_res == '下载失败':
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
        language = Language.Chinese_English
