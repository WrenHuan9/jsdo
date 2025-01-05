import os
import requests
import warnings


class CheckPacker():

    def __init__(self, projectTag, url, options):
        warnings.filterwarnings('ignore')
        self.fingerprint_html = ['<noscript', 'webpackJsonp', '<script id=\"__NEXT_DATA__', 'webpack-', '<style id=\"gatsby-inlined-css', '<div id=\"___gatsby', '<meta name=\"generator\" content=\"phoenix', '<meta name=\"generator\" content=\"Gatsby', '<meta name=\"generator\" content=\"Docusaurus']
        self.fingerprint_js = ['webpackJsonp','gulp']
        self.url = url
        self.projectTag = projectTag
        self.options = options
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"}

    def checkJS(self, projectPath):
        flag = 0
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            for filename in filenames:
                if filename != self.projectTag + ".db":
                    filePath = os.path.join(parent, filename)
                    jsOpen = open(filePath, 'r', encoding='UTF-8', errors="ignore")
                    jsFile = jsOpen.readlines()
                    jsOpen.close()
                    jsFile = str(jsFile)  # 二次转换防报错
                    if any(i in jsFile for i in self.fingerprint_js):
                        flag = 1
                        break
        return flag

    def checkHTML(self):
        headers = self.header
        url = self.url
        sslFlag = int(self.options.ssl_flag)
        if sslFlag == 1:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data, timeout=5, verify=False).text
        else:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data, timeout=5).text
        return 1 if any(i in demo for i in self.fingerprint_html) else 0

    def checkStart(self, projectPath):
        try:
            flag = self.checkHTML()
            if flag != 1:
                flag = self.checkJS(projectPath)
        except:
            flag = 777
        return flag