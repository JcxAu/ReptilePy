import tkinter as tk, tkinter.messagebox
import Get_date_html, Change_ini, Get_date_img, Language
import sys, threading, queue, time, webbrowser

language = Language.SimplifiedChinese_SimplifiedChinese
language_code = 'Chinese'
num_win_open = False
about_win_open = False
mode_win_open = False
help_win_open = False
if_download = False

# 保存下载模式


def save_mode(mode: str):
    Change_ini.start()  # 打开 ini 文件，并做好准备工作
    Change_ini.change_download_mode(mode)  # 改变下载模式
    Change_ini.save_set_up()  # 保存设置

    # 改变标签内容
    if mode == 'HTML':
        word = language['目前的下载设置为: 通过图片所在的网页获取']
    elif mode == 'IMG':
        word = language['目前的下载设置为: 通过图片自身的网址获取']
    else:
        word = language['暂无']

    lab['text'] = word

# 保存 ssl 证书验证是否开启


def ssl_open():
    if not if_download:
        Change_ini.start()
        ssl_state = Change_ini.ask_value('ssl_open_state')  # 查询 ssl 是否开启

        # 询问并展示状态
        if ssl_state == 'True':
            ssl_state = language['开启']
        else:
            ssl_state = language['关闭']

        yesno = tk.messagebox.askyesno(title=language['选择'], message=language['是否启用SSL证书验证 ?\n'] + language['现在的状态为: '] + ssl_state)

        # 保存设置
        Change_ini.start()
        Change_ini.change_ssl_open_state(yesno)
        Change_ini.save_set_up()

# 爬虫的准备工作


def prepare_reptile() -> list:
    result = []
    Change_ini.start()

    # 查询下载数量
    download_num = Change_ini.ask_value('download_num')
    if download_num == language['暂无']:
        download_num = 0
    else:
        download_num = int(download_num)
    result.append(download_num)

    # 查询下载模式
    mode = Change_ini.ask_value('download_mode')
    result.append(mode)

    # 查询是否开启 ssl
    ssl_state = Change_ini.ask_value('ssl_open_state')
    if ssl_state == 'True':
        ssl_state = True
    else:
        ssl_state = False
    result.append(ssl_state)

    return result

# 使用 IMG 模式的爬虫


def reptile_img(url: str, download_num: int, lock_n, ssl: bool = True, time_sleep: float = 0.2):
    info = Get_date_img.get_date_img(url, download_num, lock_n, time_sleep, ssl)
    download_info.put(info)


# 使用 HTML 模式的爬虫


def reptile_html(url: str, download_num: int, lock_n, ssl: bool = True, time_sleep: float = 0.2):
    info = Get_date_html.get_date_html(url, download_num, lock_n, time_sleep, ssl)
    download_info.put(info)

# 爬虫线程


def reptile_thread(url: str, download_num: int, mode: str, name: str, time_sleep: float = 0.2, ssl: bool = True):
    if mode == 'HTML':
        thread = threading.Thread(target=reptile_html, args=(url, download_num, lock, ssl, time_sleep), name=name, daemon=True)
        thread.start()
    else:
        thread = threading.Thread(target=reptile_img, args=(url, download_num, lock, ssl, time_sleep), name=name, daemon=True)
        thread.start()

# 控制爬虫线程


def reptile_threads(url: str):
    global if_download
    res = prepare_reptile()
    if res[1] == 'HTML' or res[1] == 'IMG':
        if res[0] <= 18:
            for i in range(0, res[0]):
                reptile_thread(url, 1, res[1], 'reptile_' + str(i), 0.5, res[2])
        else:
            num = int(res[0] / 18)
            residue = res[0] - num * 18
            for i in range(0, residue):
                reptile_thread(url, num + 1, res[1], 'reptile_' + str(i), res[2])
            for i in range(residue, 18):
                reptile_thread(url, num, res[1], 'reptile_' + str(i), 0.5, res[2])
    else:
        tkinter.messagebox.showwarning(title=language['唔...要不还是都爬吧'], message=language['   请设置下载模式 !   '])

        ent['state'] = 'normal'
        m_lab.grid_remove()
        but.grid(padx=40, pady=5)
        if_download = False


# 开始爬取图片


def start_reptile():
    global ent, but, if_download
    if_download = True

    ent_content = ent.get()  # 获得 url
    if ent_content != '':
        ent.delete(0, tkinter.END)  # 清空输入框的内容
        ent['state'] = 'disable'  # 输入框禁止输入
        but.grid_remove()  # 隐藏按钮
        m_lab.grid(padx=(45, 30), pady=(5, 20))  # 显示下载提示语

        reptile_threads(ent_content)
    else:
        tkinter.messagebox.showwarning(title=language['不给 URL 怎么下载 ?'], message=language['     请输入一个 URL !     '])
        if_download = False

# 关闭"询问模式"的窗口


def mode_win_open_f():
    global mode_win_open
    mode_win_open = False
    try:
        mode_win.destroy()
    except tkinter.TclError:
        pass

# 关闭"询问下载数量"的窗口


def num_win_open_f():
    global num_win_open
    num_win_open = False
    try:
        num_win.destroy()
    except tkinter.TclError:
        pass

# 关闭"关于"的窗口


def about_win_open_f():
    global about_win_open
    about_win_open = False
    try:
        about_win.destroy()
    except tkinter.TclError:
        pass

# 关闭"帮助"的窗口


def help_win_open_f():
    global help_win_open
    help_win_open = False
    try:
        help_win.destroy()
    except tkinter.TclError:
        pass

# 关闭主窗口


def destroy():
    if not if_download:
        sys.exit(0)

# 保存下载数量


def get_num():
    try:
        download_num = ent2.get()  # 获得输入框的内容
        download_num = float(download_num)  # 转换成 float 类型
        download_num = int(download_num)  # 转换成 int 类型
        if download_num < 0:
            tkinter.messagebox.showerror(title=language['下...下载负数张图片!?'], message=language['   不能填负数哦 !   '])
            download_num = 0

        # 保存设置
        Change_ini.start()
        Change_ini.change_download_num(download_num)
        Change_ini.save_set_up()
    except ValueError:
        tkinter.messagebox.showerror(title=language['你是认真的吗 ?'], message=language['  请输入数字 !  '])

# "询问下载数量"的主窗口


def num_download():
    global ent2, num_win_open, num_win
    if not if_download:
        if not num_win_open:  # 确保只能开启一个窗口
            num_win_open = True
            # 各种长宽的初始值 (适用于简体中文）
            num_win_w_h = '300x135'
            w = 300
            h = 135
            l_w = 30
            l_h = 3
            b_w = 7
            b_h = 2
            ent2_p_x = (25, 5)
            ent2_w = 20

            if language_code == 'English':
                num_win_w_h = '350x135'
                w = 350
                l_w = 40
                b_w = 9
                ent2_p_x = (30, 5)
                ent2_w = 24

            # 准备窗口
            num_win = tk.Toplevel(window)
            num_win.title(language['请输入下载的数量'])
            num_win.geometry(num_win_w_h)
            num_win.maxsize(width=w, height=h)
            num_win.minsize(width=w, height=h)
            num_win.protocol('WM_DELETE_WINDOW', num_win_open_f)

            # 标签展示下载的数量
            Change_ini.start()
            res = Change_ini.ask_value('download_num')
            label = tk.Label(num_win, text=language['目前设置的下载数量为: '] + res, width=l_w, height=l_h)
            label.grid(row=0, column=0, columnspan=2, padx=(20, 10), pady=(5, 0))

            # 输入框
            ent2 = tk.Entry(num_win, show=None, width=ent2_w)
            ent2.grid(row=1, column=0, ipadx=10, ipady=5, padx=ent2_p_x, pady=(3, 5))

            # 按钮
            button = tk.Button(num_win, text=language['确定'], width=b_w, height=b_h, command=lambda: [get_num(), num_win_open_f()])
            button.grid(row=1, column=1, padx=(7, 15), pady=(3, 5))

            num_win.mainloop()
        else:
            tkinter.messagebox.showinfo(title=language['欸嘿, 还是我技高一筹 !'], message=language['只能打开一个窗口哦 !'])

# "关于"主窗口


def about():
    global about_win_open, about_win
    if not if_download:
        if not about_win_open:  # 确保只能开启一个窗口
            about_win_open = True

            # 准备窗口
            about_win = tk.Toplevel(window)
            about_win.title(language['关于'])
            about_win.geometry('340x150')
            about_win.maxsize(width=340, height=150)
            about_win.minsize(width=340, height=150)

            # 标签展示 ( 展示项目主页网址 )
            lab1 = tk.Label(about_win, text='The GitHub homepage for this program:\nhttps://github.com/JcxAu/ReptilePy', height=2, width=34)
            lab1.grid(row=0, column=0, padx=(20, 0), pady=(10, 3))

            # 跳转按钮 ( 跳转到项目主页 )
            but1 = tk.Button(about_win, text='Access', width=7, height=1, relief='flat', command=lambda: webbrowser.open('https://github.com/JcxAu/ReptilePy'))
            but1.grid(row=0, column=1, padx=(0, 10), pady=(10, 3))

            # 标签 ( 展示开源协议 )
            lab2 = tk.Label(about_win, text='Licensing:\nBSD 3', height=2, width=10)
            lab2.grid(row=1, column=0, padx=(20, 0), pady=(3, 3))

            # 按钮 ( 跳转到开源协议 )
            but2 = tk.Button(about_win, text='View', width=7, height=1, relief='flat', command=lambda: webbrowser.open('https://github.com/JcxAu/ReptilePy/blob/main/LICENSE'))
            but2.grid(row=1, column=1, padx=(0, 10), pady=(3, 3))

            # 版本信息
            lab3 = tk.Label(about_win, text='Version information: ReptilePy-Stable-Ver1.2', height=2, width=39)
            lab3.grid(row=2, column=0, columnspan=2, padx=(20, 5), pady=(2, 10))

            about_win.protocol('WM_DELETE_WINDOW', about_win_open_f)
            about_win.mainloop()

# "询问下载模式"主窗口


def download_mode():
    global mode_win_open, lab, mode_win
    if not if_download:
        if not mode_win_open:  # 确保只能开启一个窗口
            mode_win_open = True
            # 各种长宽的初始值 (适用于简体中文）
            mode_win_w_h = '300x150'
            w = 300
            h = 150
            l_w = 42
            l_h = 3
            r_p_x = (5, 25)
            r1_p_x = r_p_x
            r_p_y = (3, 1)
            r1_p_y = (1, 3)

            if language_code == 'English':
                mode_win_w_h = '430x150'
                w = 430
                l_w = 52
                r_p_x = (10, 5)
                r1_p_x = r_p_x

            # 准备窗口
            mode_win = tk.Toplevel(window)
            mode_win.title(language['请选择下载的模式'])
            mode_win.geometry(mode_win_w_h)
            mode_win.maxsize(width=w, height=h)
            mode_win.minsize(width=w, height=h)
            mode_win.protocol('WM_DELETE_WINDOW', mode_win_open_f)

            # 关联字符串变量
            s = tk.StringVar(mode_win)

            # 查询下载模式
            Change_ini.start()
            ssl_state = Change_ini.ask_value('download_mode')

            if ssl_state == 'HTML':
                show = language['通过图片所在的网页获取']
            elif ssl_state == 'IMG':
                show = language['通过图片自身的网址获取']
            else:
                show = language['暂无']

            # 标签展示
            lab = tk.Label(mode_win, text=language['目前的下载设置为: '] + show, width=l_w, height=l_h)
            lab.grid(row=0, column=0, padx=(10, 15))

            # 改变字符串的值
            s.set(ssl_state)

            # 俩个选项
            ra_but = tk.Radiobutton(mode_win, text=language['通过图片所在的网页获取'], variable=s, value='HTML', command=lambda: save_mode(s.get()))
            ra_but.grid(row=1, column=0, padx=r_p_x, pady=r_p_y)
            ra_but1 = tk.Radiobutton(mode_win, text=language['通过图片自身的网址获取'], variable=s, value='IMG', command=lambda: save_mode(s.get()))
            ra_but1.grid(row=2, column=0, padx=r1_p_x, pady=r1_p_y)

            mode_win.mainloop()
        else:
            tkinter.messagebox.showinfo(title=language['惊不惊喜, 意不意外 ?'], message=language['只能打开一个窗口哦 !'])

# "帮助" 主窗口


def help_usr():
    global help_win_open, help_win
    if not if_download:
        if not help_win_open:  # 确保只能开启一个窗口
            help_win_open = True
            # 各种长宽的初始值 (适用于简体中文)
            help_win_w_h = '360x150'
            w = 360
            h = 150
            l_w = 48
            l_h = 8

            if language_code == 'English':
                help_win_w_h = '380x150'
                w = 380
                l_w = 50

            # 准备窗口
            help_win = tk.Toplevel(window)
            help_win.title(language['帮助'])
            help_win.geometry(help_win_w_h)
            help_win.maxsize(width=w, height=h)
            help_win.minsize(width=w, height=h)

            # 标签展示
            label = tk.Label(help_win, text=language['请先进行下载数量, 下载模式的设置。\n如果出错了, 可以先切换下载模式, 再尝试。\n注意:\n设置语言选项会使程序退出, 再启动程序, 更改便会生效。'], height=l_h, width=l_w)
            label.grid(row=0, column=0, padx=(15, 5))

            help_win.protocol('WM_DELETE_WINDOW', help_win_open_f)
            help_win.mainloop()

# 侦测器


def detector():
    global if_download
    while True:
        error_num = 0

        Change_ini.start()
        # 查询下载数量
        download_num = Change_ini.ask_value('download_num')
        if download_num == language['暂无']:
            download_num = 0
        else:
            download_num = int(download_num)

        if if_download:
            if download_info.qsize() == download_num or download_info.qsize() == 18:
                if download_num != 0:
                    if download_num > 18:
                        loop_times = 18
                    else:
                        loop_times = download_num

                    for i in range(0, loop_times):
                        try:
                            download_res = download_info.get(False)
                            error_num += download_res
                        except queue.Empty:
                            break

                    tkinter.messagebox.showinfo(title=language['下载报告'], message=language['成功: '] + str(download_num - error_num) + ' / ' + language['失败: '] + str(error_num))
                else:
                    tkinter.messagebox.showwarning(title=language['嗯? 没有下载吗 ?'], message=language['下载次数不能为 0 哦'])

                ent['state'] = 'normal'
                m_lab.grid_remove()
                but.grid(padx=40, pady=5)

                if_download = False

        time.sleep(0.2)

# 改变语言为简体中文


def language_chinese():
    if not if_download:
        Change_ini.start()
        result = Change_ini.ask_value('language')
        if result != Change_ini.language['暂无'] and result != 'Chinese':
            Change_ini.change_language('Chinese')
            Change_ini.save_set_up()

            destroy()

# 改变语言为英语


def language_english():
    if not if_download:
        Change_ini.start()
        result = Change_ini.ask_value('language')
        if result != 'English':
            Change_ini.change_language('English')
            Change_ini.save_set_up()

            destroy()

# 强制退出程序


def forced_exit():
    sys.exit(-1)


if __name__ == '__main__':
    # 各种长宽的初始值 (适用于简体中文)
    w_h = '300x150'
    but_w = 8
    but_h = 3
    m_l_w = 13
    m_l_h = 2

    # 查询语言
    Change_ini.start()
    res = Change_ini.ask_value('language')
    if res != Change_ini.language['暂无']:
        if res == 'English':
            language = Language.SimplifiedChinese_English
            language_code = 'English'

            w_h = '300x170'
            but_w = 15
            but_h = 3
            m_l_w = 23

    # 创建互斥锁
    lock = threading.Lock()

    # 创立队列
    download_info = queue.Queue()

    # 创建侦测器线程
    detector_thread = threading.Thread(target=detector, name='detector', daemon=True)
    detector_thread.start()

    # 准备主窗口
    window = tk.Tk()
    window.geometry(w_h)
    window.title('ReptilePy')
    window.maxsize(width=300, height=150)
    window.minsize(width=300, height=150)

    # 准备主菜单
    main_menu = tk.Menu(window)
    download_setting_menu = tk.Menu(main_menu, tearoff=0)
    language_menu = tk.Menu(main_menu, tearoff=0)

    # 加入主菜单
    main_menu.add_cascade(label=language['下载设置'], menu=download_setting_menu)
    main_menu.add_command(label=language['帮助'], command=help_usr)
    main_menu.add_command(label=language['关于'], command=about)
    main_menu.add_cascade(label=language['语言'], menu=language_menu)
    main_menu.add_command(label=language['退出'], command=destroy)
    main_menu.add_command(label=language['强制退出'], command=forced_exit)

    # 加入 "download_setting_menu" 的二级菜单
    download_setting_menu.add_command(label=language['下载数量'], command=num_download)
    download_setting_menu.add_command(label=language['下载模式选择'], command=download_mode)
    download_setting_menu.add_command(label=language['SSL证书启用'], command=ssl_open)

    # 加入 "language_menu" 的二级菜单
    language_menu.add_command(label='简体中文', command=language_chinese)
    language_menu.add_command(label='English', command=language_english)

    # 窗口设置
    window.config(menu=main_menu)

    # 输入 url 的输入框
    ent = tk.Entry(window, show=None)
    ent.grid(row=0, column=0, ipadx=30, ipady=5, padx=(45, 30), pady=(20, 10))

    # 下载中的提示语
    m_lab = tk.Label(window, text=language['下载中, 请稍候...'], width=m_l_w, height=m_l_h)
    m_lab.grid(row=1, column=0, padx=(45, 30), pady=(5, 20))
    m_lab.grid_remove()

    # 确认按钮
    but = tk.Button(window, text=language['确认爬取'], width=but_w, height=but_h, command=start_reptile)
    but.grid(row=1, column=0, padx=(45, 30), pady=(5, 20))

    # 当点击 "x" 的时候执行的函数
    window.protocol('WM_DELETE_WINDOW', destroy)
    # 主界面事件循环
    window.mainloop()
