import requests, os, io, time
from PIL import Image
import Log, Language, Change_ini

ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}
pic_num = 0
language = Language.SimplifiedChinese_SimplifiedChinese

# 下载图片


def download_img(url: str, ua: dict, lock, ssl: bool = True) -> dict:
    res_d: dict = {'state': None, 'info': None}
    try:
        get_data = requests.get(url, headers=ua, timeout=(5, 7), verify=ssl)
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language['图片请求失败 !']
        return res_d
    download_state = get_data.status_code
    if download_state == 200:
        try:
            data_img = get_data.content
            lock.acquire()
            bytes_img = io.BytesIO(data_img)
            im = Image.open(bytes_img)
            o = open('./photos/img' + str(pic_num) + '.' + im.format, 'wb')
            o.write(data_img)
            o.close()
            lock.release()

            res_d['state'] = '成功'
            return res_d
        except Exception:
            res_d['state'] = '失败'
            res_d['info'] = language['图片数据处理出错 !']
            return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = language['图片请求失败 !'] + language['状态码为: '] + str(download_state)
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
                i = res.find('.')  # 找到 "." 所在的索引
                pic_num_l.append(int(res[:i]))  # 将 "." 以前的内容为 str 类型的数字转换成 int 类型并加入到图片序列中
            pic_num = max(pic_num_l) + 1  # 获取最大的图片序列并加一, 得到此次开始时的图片序列
        else:
            pic_num = 0

# 爬虫算法


def reptile_algorithm(url: str, ua: dict, lock, ssl: bool = True) -> dict:
    global pic_num
    res_d: dict = {'state': None}
    if url != '' and 'http' == url[:4]:
        download_info = download_img(url, ua, lock, ssl)
        if download_info['state'] == '成功':
            lock.acquire()
            pic_num += 1
            lock.release()

            res_d['state'] = '成功'
            return res_d
        else:
            res_d['state'] = '失败'
            lock.acquire()
            Log.write_log(language['result: 下载失败, 状态为: '] + str(download_info['info']) + '\nurl: ' + str(url))
            lock.release()
            return res_d
    else:
        res_d['state'] = '失败'
        lock.acquire()
        Log.write_log(language['result: 请输入正确的URL !'] + '\nurl: ' + str(url))
        lock.release()
        return res_d

# 集成函数 (只要用这个就行了)


def get_date_img(url: str, num_download: int, lock, time_sleep: float = 0.2, ssl: bool = True) -> int:
    download_error = 0
    i = 0
    while i < int(num_download):
        find_pic_num()
        reptile_res_d = reptile_algorithm(url, ua, lock, ssl=ssl)
        if reptile_res_d['state'] == '失败':
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
