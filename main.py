#系统模块
import sys,os,subprocess
import logging

#QYPT5模块
from PyQt5 import uic,QtCore,QtGui
from PyQt5.QtWidgets import QApplication,QFileDialog,QMessageBox
import dirsearch_rc




#加载ini的模块
import configparser

logging.basicConfig(filename='debug_log.log', format='%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S ',
                    level=logging.INFO)
logger = logging.getLogger()
KZT = logging.StreamHandler()
KZT.setLevel(logging.DEBUG)
logger.addHandler(KZT)

dirsearch_dir = ""
python_dir = ""

#扩展 -e *
EXTENSIONS = " -e * "
#强制扩展 --force-extensions
force_extensions = ""
#递归 -r
recursive = " -r "
#随机UA --random_agent
random_agent = ""
#线程 -t 1
threads = ""
#延迟 --delay=10
delay = ""
#超时  --timeout=200
timeout= ""
#排除状态码 --exclude-status=200 or --exclude-status=400-500
exclude_status = ""
#排除文本 --exclude-texts="error"
exclude_texts = ""
#排除重定向 支持正则表达式（或文本）匹配 --exclude-redirect="/index.html"
exclude_redirect = ""
#排除响应包路径 --exclude-response="/index.html"
exclude_response = ""
#排除响应包大小 --exclude-sizes=”0B,4KB“
exclude_sizes = ""
#最小响应包长度 --min-response-size=1024
min_response_size =""
#最大响应包长度 --max-response-size=1024
max_response_size =""
#扫描的最大运行时间 --max_time=1 按秒算
max_time =""
#重试次数 --retries=1
retries = ""
#代理 --proxy="http://127.0.0.1:8080" or --proxy="127.0.0.1:8080" or --proxy="socks5://127.0.0.1:8080"
aproxy = ""
#HTTP请求数据 --data="a=test&b=111"  这个需要详细测试有没有bug
post_data = ""
#COOKIE --cookie='session=admin;'
cookie = ""
#auth --auth='user:pass'
auth = ""
#auth-type --auth-type='basic, digest, bearer, ntlm, jwt,oauth2'
auth_type = ""

#HTTP请求方法 --http-method=GET
http_method = ""

#自定义其他输入参数
other_pam = ""

class Stats:
    def __init__(self):
        # 从文件中加载UI定义
        file = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(file+"/ui.ui")
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        self.ui.scan_start.clicked.connect(self.set_scan_start) #开始扫描
        self.ui.select_dirsearch.clicked.connect(self.select_dirsearch)  # 点击选择工具按键的信号槽
        self.ui.select_python.clicked.connect(self.select_python)  # 点击python工具按键的信号槽
        self.ui.input_EXTENSIONS.textChanged.connect(self.set_EXTENSIONS) #点击后缀扩展输入框的信号槽
        self.ui.input_threads.textChanged.connect(self.set_threads)  # 点击线程输入框的信号槽
        self.ui.input_delay.textChanged.connect(self.set_input_delay)  # 点击延迟输入框的信号槽
        self.ui.input_timeout.textChanged.connect(self.set_input_timeout)  # 点击超时输入框的信号槽

        self.ui.force_extensions.stateChanged.connect(self.set_force_extensions)  # 点击强制扩展的信号槽
        self.ui.recursive.stateChanged.connect(self.set_recursive)  # 点击递归目录的信号槽
        self.ui.random_agent.stateChanged.connect(self.set_random_agent)  # 点击随机User-Agent的信号槽

        self.ui.input_exclude_status.textChanged.connect(self.set_exclude_status)  # 点击排除状态码输入框的信号槽
        self.ui.input_exclude_texts.textChanged.connect(self.set_exclude_texts)  # 点击排除响应文本输入框的信号槽
        self.ui.input_exclude_redirect.textChanged.connect(self.set_exclude_redirect)  # 点击排除重定向输入框的信号槽
        self.ui.input_exclude_response.textChanged.connect(self.set_exclude_response)  # 点击排除响应包路径输入框的信号槽
        self.ui.input_exclude_sizes.textChanged.connect(self.set_exclude_sizes)  # 点击排除响应包大小输入框的信号槽
        self.ui.input_min_response_size.textChanged.connect(self.set_min_response_size)  # 点击最小响应包长度输入框的信号槽
        self.ui.input_max_response_size.textChanged.connect(self.set_max_response_size)  # 点击最大响应包长度输入框的信号槽
        self.ui.input_max_time.textChanged.connect(self.set_max_time)  # 点击扫描的最大运行时间输入框的信号槽
        self.ui.input_retries.textChanged.connect(self.set_retries)  # 点击重试次数输入框的信号槽

        self.ui.input_proxy.textChanged.connect(self.set_proxy)  # 点击代理输入框的信号槽
        self.ui.auth_tips_2.clicked.connect(self.auth_tips_2)  # 点击代理提示按钮的信号槽
        self.ui.input_post_data.textChanged.connect(self.set_post_data)  # 点击POST数据输入的信号槽
        self.ui.input_cookie.textChanged.connect(self.set_cookie)  # 点击COOKIE输入的信号槽
        self.ui.input_auth.textChanged.connect(self.set_auth)  # 点击身份认证输入的信号槽
        self.ui.input_auth_type.textChanged.connect(self.set_auth_type)  # 点击身份认证属性输入的信号槽
        self.ui.auth_tips.clicked.connect(self.auth_tips)  # 点击身份认证属性提示按钮的信号槽
        self.ui.other_input.textChanged.connect(self.set_other_input)  # 点击其他参数输入框的信号槽

        self.ui.radio_GET.toggled.connect(self.set_GET)
        self.ui.radio_POST.toggled.connect(self.set_GET)
        self.ui.radio_HEAD.toggled.connect(self.set_GET)
        self.ui.radio_OPTIONS.toggled.connect(self.set_GET)
        self.ui.setFixedSize(943, 615)


        self.open_conf()  # 打开配置文件
        self.set_parameter() #调用 执行dirsearch参数 函数

    def auth_tips_2(self):
        """
        #给代理输入框添加一个固定值，或者或示范值
        socks5://127.0.0.1:10808
        http://127.0.0.1:8080
        :return:
        """
        global aproxy
        messageBox = QMessageBox()
        messageBox.setWindowTitle('提示')
        messageBox.setText('选择http还是sock5')
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = messageBox.button(QMessageBox.Yes)
        buttonY.setText('http')
        buttonN = messageBox.button(QMessageBox.No)
        buttonN.setText('sock5')
        messageBox.exec_()
        if messageBox.clickedButton() == buttonY:
            aproxy = ' --proxy="http://127.0.0.1:8080 "'
            self.ui.input_proxy.setText(str('http://127.0.0.1:8080'))
        else:
            aproxy = ' --proxy="socks5://127.0.0.1:10808 "'
            self.ui.input_proxy.setText(str('socks5://127.0.0.1:10808'))
        logging.info('设置设置代理为为 {}'.format(aproxy))
        self.set_parameter() #调用 执行dirsearch参数 函数

    # 添加中文的确认退出提示框1
    # def closeEvent(self, event):
    #     # 创建一个消息盒子（提示框）
    #     quitMsgBox = QMessageBox()
    #     # 设置提示框的标题
    #     quitMsgBox.setWindowTitle('确认提示')
    #     # 设置提示框的内容
    #     quitMsgBox.setText('你确认退出吗？')
    #     # 设置按钮标准，一个yes一个no
    #     quitMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    #     # 获取两个按钮并且修改显示文本
    #     buttonY = quitMsgBox.button(QMessageBox.Yes)
    #     buttonY.setText('确定')
    #     buttonN = quitMsgBox.button(QMessageBox.No)
    #     buttonN.setText('取消')
    #     quitMsgBox.exec_()
    #     # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用，否则就忽略关闭事件
    #     if quitMsgBox.clickedButton() == buttonY:
    #         event.accept()
    #     else:
    #         event.ignore()

    def set_other_input(self):
        """
        #其他输入参数
        :return:
        """
        global other_pam
        other_pam = str(self.ui.other_input.text())
        if other_pam !="":
            other_pam = '{}'.format(other_pam)
        else:
            other_pam = ""
        logging.info('添加自定义输入参数 {}'.format(other_pam))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_GET(self):
        global http_method
        if self.ui.radio_GET.isChecked() == True:
            http_method = " --http-method=GET "
        elif self.ui.radio_POST.isChecked() == True:
            http_method = " --http-method=POST "
        elif self.ui.radio_HEAD.isChecked() == True:
            http_method = " --http-method=HEAD "
        elif self.ui.radio_OPTIONS.isChecked() == True:
            http_method = " --http-method=OPTIONS "
        logging.info('设置HTTP请求方法为为 {}'.format(http_method))
        self.set_parameter()  # 调用 执行dirsearch参数 函数

    def auth_tips(self):
        self.show_message("身份认证属性提示","basic, digest, bearer, ntlm, jwt,oauth2 等等...")

    def set_auth_type(self):
        """
        #auth-type --auth-type='basic, digest, bearer, ntlm, jwt,oauth2'
        :return:
        """
        global auth_type
        auth_type = str(self.ui.input_auth_type.text())
        if auth_type !="" and auth_type !=' --auth-type= ':
            auth_type = ' --auth-type="{} "'.format(auth_type)
        else:
            auth_type = ""
        logging.info('设置auth_type为 {}'.format(auth_type))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_auth(self):
        """
        #auth --auth='user:pass'
        :return:
        """
        global auth
        auth = str(self.ui.input_auth.text())
        if auth !="" and auth !=' --auth= ':
            auth = ' --auth="{}" '.format(auth)
        else:
            auth = ""
        logging.info('设置auth为 {}'.format(auth))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_cookie(self):
        """
        #COOKIE --cookie='SESSIONID=123'
        :return:
        """
        global cookie
        cookie = str(self.ui.input_cookie.text())
        if cookie !="" and cookie !=' --cookie= ':
            cookie = ' --cookie="{}" '.format(cookie)
        else:
            cookie = ""
        logging.info('设置cookie为 {}'.format(cookie))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_post_data(self):
        """
        #HTTP请求数据 --data="a=test&b=111"  这个需要详细测试有没有bug
        :return:
        """
        global post_data
        post_data = str(self.ui.input_post_data.text())
        if post_data !="" and post_data !=' --data= ':
            post_data = ' --data="{}" '.format(post_data)
        else:
            post_data = ""
        logging.info('设置HTTP请求数据为 {}'.format(post_data))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_proxy(self):
        """
        #代理 --proxy="http://127.0.0.1:8080" or --proxy="127.0.0.1:8080" or --proxy="socks5://127.0.0.1:8080"
        :return:
        """
        global aproxy
        aproxy = str(self.ui.input_proxy.text())
        if aproxy !="" and aproxy !=' --proxy= ':
            aproxy = ' --proxy="{}" '.format(aproxy)
        else:
            retries = ""
        logging.info('设置代理为 {}'.format(aproxy))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_retries(self):
        """
        #重试次数 --retries=1
        :return:
        """
        global retries
        retries = str(self.ui.input_retries.text())
        if retries !="" and retries !=' --retries= ':
            retries = ' --retries={} '.format(retries)
        else:
            retries = ""
        logging.info('设置最大响应包长度为 {}'.format(retries))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_max_time(self):
        """
        #扫描的最大运行时间 --max_time=1 按秒算
        :return:
        """
        global max_time
        max_time = str(self.ui.input_max_time.text())
        if max_time !="" and max_time !=' --max-time= ':
            max_time = ' --max-time={} '.format(max_time)
        else:
            max_time = ""
        logging.info('设置扫描的最大运行时间为 {}'.format(max_time))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_max_response_size(self):
        """
        #最大响应包长度 --max-response-size=1024
        :return:
        """
        global max_response_size
        max_response_size = str(self.ui.input_max_response_size.text())
        if max_response_size !="" and max_response_size !=' --max-response-size= ':
            max_response_size = ' --max-response-size={} '.format(max_response_size)
        else:
            max_response_size = ""
        logging.info('设置最大响应包长度为 {}'.format(max_response_size))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_min_response_size(self):
        """
        #最小响应包长度 --min-response-size=1024
        :return:
        """
        global min_response_size
        min_response_size = str(self.ui.input_min_response_size.text())
        if min_response_size !="" and min_response_size !=' --min-response-size= ':
            min_response_size = ' --min-response-size={} '.format(min_response_size)
        else:
            min_response_size = ""
        logging.info('设置最小响应包长度为 {}'.format(min_response_size))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_exclude_sizes(self):
        """
        排除响应包大小 --exclude-sizes="0B,4KB"
        :return:
        """
        global exclude_sizes
        test = str(self.ui.input_exclude_sizes.text())
        exclude_sizes = test.upper()
        if exclude_sizes !="" and exclude_sizes !=' --exclude-sizes= ':
            exclude_sizes = ' --exclude-sizes="{}" '.format(exclude_sizes)
        else:
            exclude_sizes = ""
        logging.info('排除响应包大小 设置为 "{}"'.format(exclude_sizes))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_exclude_response(self):
        """
        排除响应包路径 --exclude-response="/index.html"
        :return:
        """
        global exclude_response
        exclude_response = self.ui.input_exclude_response.text()
        if exclude_response !="" and exclude_response !=' --exclude-response= ':
            exclude_response = ' --exclude-response="{}" '.format(exclude_response)
        else:
            exclude_texts = ""
        logging.info('排除响应包路径 设置为 "{}"'.format(exclude_response))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_exclude_redirect(self):
        """
        排除重定向 --exclude-redirect="/index.html"
        :return:
        """
        global exclude_redirect
        exclude_redirect = self.ui.input_exclude_redirect.text()
        if exclude_redirect !="" and exclude_redirect !='--exclude-redirect= ':
            exclude_redirect = ' --exclude-redirect="{}" '.format(exclude_redirect)
        else:
            exclude_texts = ""
        logging.info('排除重定向 设置为 "{}"'.format(exclude_redirect))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_exclude_texts(self):
        """
        排除响应包文本 --exclude-texts="error"
        :return:
        """
        global exclude_texts
        exclude_texts = self.ui.input_exclude_texts.text()
        if exclude_texts !="" and exclude_texts !=" --exclude-texts= ":
            exclude_texts = " --exclude-texts={} ".format(exclude_texts)
        else:
            exclude_texts = ""
        logging.info("排除响应包文本 设置为 {}".format(exclude_texts))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_exclude_status(self):
        """
        排除状态码函数 --exclude-status=500 or ----exclude-status=400-499 ...
        :return:
        """
        global exclude_status
        exclude_status = self.ui.input_exclude_status.text()
        if exclude_status !="" and exclude_status !=" --exclude-status= ":
            exclude_status = " --exclude-status={} ".format(exclude_status)
        else:
            exclude_status = ""
        logging.info("排除状态码 设置为 {}".format(exclude_status))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_input_timeout(self):
        """
        超时函数 --timeout=10 or --delay=100 ...
        :return:
        """
        global timeout
        timeout = self.ui.input_timeout.text()
        if timeout !="" and timeout !=" --timeout= ":
            timeout = " --timeout={} ".format(timeout)
        else:
            timeout = ""
        logging.info("超时 设置为 {}".format(timeout))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_input_delay(self):
        """
        延迟函数 --delay=1 or --delay=10 ...
        :return:
        """
        global delay
        delay = self.ui.input_delay.text()
        if delay !="" and delay !=" --delay= ":
            delay = " --delay={} ".format(delay)
        else:
            delay = ""
        logging.info("延迟 设置为 {}".format(delay))
        self.set_parameter() #调用 执行dirsearch参数 函数


    def set_random_agent(self):
        global random_agent
        """
        随机UA函数 --random-agent
        """
        isChecked = self.ui.random_agent.isChecked()
        if isChecked == True:
            random_agent = " --random-agent "
            logging.info("随机User-Agent 设置为 --random-agent 开启 ")
        else:
            random_agent = ""
            logging.info("随机User-Agent 设置为  关闭 ")
        self.set_parameter()  # 调用 执行dirsearch参数 函数

    def set_force_extensions(self):
        """
        强制后缀扩展函数 --force-extensions
        :return:
        """
        global force_extensions
        isChecked = self.ui.force_extensions.isChecked()
        if isChecked == True:
            force_extensions = " --force-extensions "
            logging.info("强制扩展后缀 设置为 --force-extensions 开启 ")
        else:
            force_extensions = ""
            logging.info("强制扩展后缀 设置为  关闭 ")
        self.set_parameter()  # 调用 执行dirsearch参数 函数

    def set_recursive(self):
        """
        目录扫描递归函数 -r
        :return:
        """
        global recursive
        isChecked = self.ui.recursive.isChecked()
        if isChecked == True:
            recursive = " -r "
            logging.info("目录递归扫描 设置为 -r 开启 ")
        else:
            recursive = ""
            logging.info("目录递归扫描 设置为  关闭 ")
        self.set_parameter()  # 调用 执行dirsearch参数 函数

    def set_threads(self):
        """
        线程函数 -t 1 or -t 10 ...
        :return:
        """
        global threads
        threads = self.ui.input_threads.text()
        if threads !="" and threads !=" -t ":
            threads = " -t {} ".format(threads)
        else:
            threads = ""
        logging.info("线程 设置为 {}".format(threads))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_EXTENSIONS(self):
        """
        后缀扩展 -e * or -e php,jsp,html ...
        :return:
        """
        global EXTENSIONS
        EXTENSIONS = self.ui.input_EXTENSIONS.text()
        if EXTENSIONS !="" and EXTENSIONS !=" -e " and EXTENSIONS !=" ":
            EXTENSIONS = " -e {} ".format(EXTENSIONS)
        else:
            EXTENSIONS = " -e * "
        logging.info("后缀扩展设置为 {}".format(EXTENSIONS))
        self.set_parameter() #调用 执行dirsearch参数 函数

    def set_parameter(self):
        """
        执行参数设置，包括参数栏
        :return:
        """
        global EXTENSIONS,force_extensions,recursive,random_agent,threads,delay,timeout,exclude_status,exclude_texts,exclude_redirect,exclude_response,exclude_sizes,min_response_size,max_response_size,max_time,retries,aproxy,post_data,cookie,auth_type,auth,http_method,other_pam
        parameter = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(EXTENSIONS,force_extensions,recursive,random_agent,threads,delay,timeout,exclude_status,exclude_texts,exclude_redirect,exclude_response,exclude_sizes,min_response_size,max_response_size,max_time,retries,aproxy,post_data,cookie,auth_type,auth,http_method,other_pam)
        self.ui.parameter.setText(str(parameter))  # 获取参数输入框的内容


    def set_scan_start(self):
        """
        点击开始扫描按钮
        :return:
        """
        global dirsearch_dir,python_dir
        parameter = self.ui.parameter.text()#获取参数输入框的内容
        pythontest = self.ui.input_python.text()
        if (dirsearch_dir !="" and python_dir !="") or (dirsearch_dir !="" and pythontest !="")  :
            if self.ui.input_url.text() != "":
                if "：" or "，" or "“" in str(parameter):
                    parameter = parameter.replace("：",":")
                    parameter = parameter.replace("，", ",")
                    parameter = parameter.replace("”", "\"")
                    self.ui.parameter.setText(str(parameter))
                    logging.info("发现输入了，“：其中的大写字符，已转换")
                url = "-u {}".format(self.ui.input_url.text())  # 获取url输入框的内容
                logger.info("开始扫描：命令如下：{} {} {} {} ".format(python_dir, dirsearch_dir, url, parameter))
                os.system("  start cmd /k {} {} {} {}".format(python_dir, dirsearch_dir, url, parameter))
                # subprocess.call("cmd/k start  {} {} {} {}".format(python_dir, dirsearch_dir, url, parameter),
                #                 shell=False)
                # output = subprocess.call(["powershell C:\\pyqt\\packed\\1.ps1"] )
                # os.system(" start cmd C:\\pyqt\\packed\\1.ps1")
            else:
                self.show_message("提示", "请输入URL")
        else:
            self.show_message("提示", "请选择环境参数")


    def open_conf(self):
        """
        打开conf文件，没有则创建
        :return:
        """
        global dirsearch_dir,python_dir
        conf = configparser.ConfigParser()
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        conf_file = "{}\\dirsearch_conf.ini".format(application_path)
        logging.info("conf文件位置{}".format(conf_file))
        if os.path.exists(conf_file):
            logger.info("正在加载conf文件{}".format(conf_file))
            conf.read(filenames=conf_file)
            dirsearch_dir = conf.get(section='Path', option='dirsearch')
            python_dir = conf.get(section='Path', option='python')
            if dirsearch_dir != '' and python_dir!= '':
                logger.info("正在加载dirsearch文件{}".format(dirsearch_dir))
                logger.info("正在加载python文件{}".format(python_dir))
                self.ui.input_dirsearch.setText(str(dirsearch_dir))
                self.ui.input_python.setText(str(python_dir))

    def WriteConf(self):
        """
        写入dirsearch_conf.ini文件的函数,如果文件存在则不写入
        :param
        :return:
        """
        global dirsearch_dir,python_dir
        conf = configparser.ConfigParser()
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        WorkDir = "{}\\dirsearch_conf.ini".format(application_path)
        f = open(WorkDir, "w+")
        f.write("[Path]\n")
        f.write('dirsearch = {}\n'.format(dirsearch_dir))
        f.write('python = {}\n'.format(python_dir))
        f.close()
        logging.info("写入conf文件成功：{} = {}".format(dirsearch_dir,python_dir))

    def select_dirsearch(self):
        """
        选择dirsearch目录，并且修改input_dirsearch的内容
        :return:
        """
        global dirsearch_dir
        dir = QFileDialog.getOpenFileName(None, "选取文件", "./", "python Files (*.py)")[0]
        logger.info("选择的dirsearch文件是{}".format(dir))
        dirsearch_dir = dir
        self.WriteConf()
        self.ui.input_dirsearch.setText(str(dir))
        return


    def select_python(self):
        """
        选择python文件，并且修改input_python的内容
        :return:
        """
        global python_dir
        dir = QFileDialog.getOpenFileName(None, "选取文件", "./", "exe Files (*.exe)")[0]
        logger.info("选择的python文件是{}".format(dir))
        python_dir = dir
        self.WriteConf()
        self.ui.input_python.setText(str(dir))
        return

    def show_message(self,title,message):
        """
        提示框函数
        :param title: 传入的标题
        :param message: 传入的提示信息
        :return:
        """
        QMessageBox.information(self.ui, title, message,QMessageBox.Yes)  # 最后的Yes表示弹框的按钮显示为Yes，默认按钮显示为OK,不填QMessageBox.Yes即为默认

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    App = QApplication(sys.argv)    # 创建QApplication对象，作为GUI主程序入口
    stats = Stats()
    # apply_stylesheet(App, theme='light_blue.xml')
    stats.ui.show()               # 显示主窗体
    sys.exit(App.exec_())   # 循环中等待退出程序
