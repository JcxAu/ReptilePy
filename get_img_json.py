import requests, io, language, os, time
import log, change_ini
from PIL import Image

ua: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}
language_d: dict = language.SimplifiedChinese_SimplifiedChinese
pic_num: int = 0
log_file_name = change_ini.log_file_name


def get_json(url: str, headers: dict, ssl: bool = True) -> dict:
    res_d: dict = {'state': None, 'info': None, 'json_data': None}
    try:
        result = requests.get(url, headers=headers, verify=ssl, timeout=(5, 7))
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language_d['请求超时 !']
        return res_d
    if result.status_code == 200:
        res_d['state'] = '成功'
        res_d['json_data'] = result.json()
        return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = language_d['状态码为: '] + str(result.status_code)
        return res_d


def find_url_from_json(url: str, headers: dict, ssl: bool = True) -> dict:
    res_d: dict = {'state': None, 'info': None, 'url': None}
    result = get_json(url, headers, ssl)
    if result['state'] == '成功':
        json_data = result['json_data']
        res_d = find_url_algorithm(json_data)
        return res_d
    else:
        res_d['state'] = '失败'
        res_d['info'] = result['info']
        return res_d

# 解析 JSON 的算法


def find_url_algorithm(json_data: "dict or list") -> dict:
    res_d: dict = {'state': None, 'info': None, 'url': None}
    if type(json_data) == dict:
        if 'url' in json_data:
            res_d['url'] = json_data['url']
            res_d['state'] = '成功'
            return res_d

        elif 'urls' in json_data:
            if type(json_data['urls']) == list:
                if json_data['urls']:
                    res_d['url'] = json_data['urls'][0]
                    res_d['state'] = '成功'
                    return res_d

            elif type(json_data['urls']) == dict:
                urls = []
                for i in json_data['urls']:
                    urls.append(json_data['urls'][i])
                res_d['url'] = urls[0]
                res_d['state'] = '成功'
                return res_d

        else:
            is_dict_or_list = []
            for i in json_data:
                if type(json_data[i]) == dict:
                    is_dict_or_list.append(json_data[i])

                elif type(json_data[i]) == list:
                    is_dict_or_list.append(json_data[i])

            if is_dict_or_list:
                for i in is_dict_or_list:
                    res = find_url_algorithm(i)
                    if (res is not None) and (res['state'] == '成功' and res['url'] is not None):
                        return res

                    else:
                        res_d['state'] = '失败'
                        res_d['info'] = language_d['没有发现图片的网址 !']
                        return res_d

            else:
                res_d['state'] = '失败'
                res_d['info'] = language_d['没有发现图片的网址 !']
                return res_d

    elif type(json_data) == list:
        is_dict_or_list = []
        for i in json_data:
            if type(i) == dict:
                is_dict_or_list.append(i)

            elif type(i) == list:
                is_dict_or_list.append(i)

        if is_dict_or_list:
            for i in is_dict_or_list:
                res = find_url_algorithm(i)
                if (res is not None) and (res['state'] == '成功' and res['url'] is not None):
                    return res

                else:
                    res_d['state'] = '失败'
                    res_d['info'] = language_d['没有发现图片的网址 !']
                    return res_d

        else:
            res_d['state'] = '失败'
            res_d['info'] = language_d['没有发现图片的网址 !']
            return res_d


def download_img(url: str, ua: dict, ssl: bool = True) -> dict:
    res_d: dict = {'state': None, 'info': None}
    try:
        get_data = requests.get(url, headers=ua, timeout=(5, 7), verify=ssl)
    except requests.exceptions.RequestException:
        res_d['state'] = '失败'
        res_d['info'] = language_d['图片请求失败 !']
        return res_d
    download_state = get_data.status_code
    if download_state == 200:
        try:
            data_img = get_data.content
            bytes_img = io.BytesIO(data_img)
            im = Image.open(bytes_img)
            f = open('./photos/img' + str(pic_num) + '.' + im.format, 'wb')
            f.write(data_img)
            f.close()

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


def reptile_algorithm(url: str, headers: dict, ssl: bool = True) -> dict:
    global pic_num
    res_d = {'state': None}

    if url != '' and ('http://' in url[:7] or 'https://' in url[:8]):
        img_url_d = find_url_from_json(url, headers, ssl)
        if img_url_d['state'] == '成功':
            download_info = download_img(img_url_d['url'], headers, ssl)
            if download_info['state'] == '成功':
                pic_num += 1

                res_d['state'] = '成功'
                return res_d

            else:
                res_d['state'] = '失败'
                log.write_log(language_d['result: 下载失败, 状态为: '] + str(download_info['info']) + '\nurl: ' + str(url), file_name=log_file_name)
                return res_d
        else:
            res_d['state'] = '失败'
            log.write_log('result: ' + language_d['图片请求失败 !'] + str(img_url_d['info']) + '\nurl: ' + str(url), file_name=log_file_name)
            return res_d

    else:
        res_d['state'] = '失败'
        log.write_log(language_d['result: 请输入正确的URL !'] + '\nurl: ' + str(url), file_name=log_file_name)
        return res_d


def get_img_json(url: str, num_download: int, lock, time_sleep: float = 0.2, ssl: bool = True) -> dict:
    res_d = {'success': 0, 'error': 0}
    error: int = 0
    success: int = 0
    i = 0
    while i < int(num_download):
        find_pic_num()
        lock.acquire()
        result = reptile_algorithm(url, ua, ssl=ssl)
        lock.release()
        if result['state'] == '失败':
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
