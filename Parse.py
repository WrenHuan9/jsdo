import re
import requests
import warnings
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from DownloadJs import DownloadJs
from utils import Utils


class ParseMainPage():

    def __init__(self, projectTag, projectPath, url, options):
        warnings.filterwarnings('ignore')
        self.url = url
        self.jsPaths = []
        self.jsRealPaths = []
        self.jsPathList = []
        self.options = options
        self.projectTag = projectTag
        self.projectPath = projectPath
        self.proxy_data = {'http': self.options.proxy, 'https': self.options.proxy}
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
        }

    def requestUrl(self):
        headers = self.header
        url = self.url
        print(Utils().tellTime() + "目标站点：" + url)
        print(Utils().tellTime() + "正在解析网页中...")
        sslFlag = int(self.options.ssl_flag)
        if sslFlag == 1:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data, timeout=30, verify=False)
        else:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data, timeout=30)
        # 重定向和跳转修正
        self.url = demo.url
        demo = demo.text.replace("<!--", "").replace("-->", "")
        soup = BeautifulSoup(demo, "html.parser")
        # 主页面js提取
        for item in soup.find_all("script"):
            jsPath = item.get("src")
            if jsPath:
                self.jsPaths.append(jsPath)
        # 防止使用link标签情况
        for item in soup.find_all("link"):
            jsPath = item.get("href")
            try:
                if jsPath[-2:] == "js":  # 防止提取css
                    self.jsPaths.append(jsPath)
            except:
                pass
        try:
            self.dealJs(self.jsPaths)
            print(Utils().tellTime() + "dealjs函数正常")
        except Exception as e:
            print("[Err] %s" % e)

    def dealJs(self, js_paths):  # 生成js绝对路径
        res = urlparse(self.url)  # 处理url多余部分
        baseUrl = Utils().getBaseUrl(self.url)
        self.jsRealPaths = Utils().generateFullPath(js_paths, baseUrl, res)
        print(Utils().tellTime() + "网页解析完毕，共发现" + str(len(self.jsRealPaths)) + "个JS文件")
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_")
        DownloadJs(js_paths, self.jsRealPaths, self.options, self.url).downloadJs(self.projectPath, False)

    def scriptCrawling(self, demo):
        # 将站点主入口作为string再次处理一遍，如果存在遗漏，则将主入口js作为文件保存到工作目录中，返回从中提取的其他js路径
        scriptInside = ""
        soup = BeautifulSoup(demo, "html.parser")
        for item in soup.find_all("script"):
            scriptString = str(item.string)  # 防止特殊情况报错
            listSrc = re.findall(r'src=\"(.*?)\.js', scriptString)
            if not listSrc == []:
                for jsPath in listSrc:
                    self.jsPathList.append(jsPath)
            if scriptString != "None":  # None被转成字符串了
                scriptInside = scriptInside + scriptString
        if scriptInside != "":
            DownloadJs(self.jsPaths, self.jsRealPaths, self.options, self.url).creatInsideJs(self.projectPath, Utils().creatTag(6), scriptInside)
        return self.jsPathList

    def parseMainPageStart(self):
        self.requestUrl()
        return self.url