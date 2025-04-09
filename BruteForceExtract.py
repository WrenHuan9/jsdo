from urllib.parse import urlparse

import node_vm2
import os
import re

from DownloadJs import DownloadJs
from utils import Utils


class BruteForceExtract():

    def __init__(self, projectTag, baseUrl, options, originalPaths):
        self.name_list = []
        self.baseUrl = baseUrl
        self.jsFileNames = []
        self.localFileNames = []
        self.js_compile_results = []
        self.projectTag = projectTag
        self.options = options
        self.originalPaths = originalPaths

    def checkCode(self, jsFilePath, projectPath):
        jsOpen = open(jsFilePath, 'r', encoding='UTF-8', errors="ignore")
        jsFile = jsOpen.readlines()
        jsOpen.close()
        jsFile = str(jsFile)
        pattern = re.compile(r"\/([a-zA-Z_0-9\.\-]+)\.js", re.DOTALL)
        jsPaths = pattern.findall(jsFile)
        if jsPaths:
            path = projectPath[:-1] + "_result.txt"
            with open(path, "w+") as file:
                for jsPath in jsPaths:
                    jsPath = jsPath + ".js"
                    file.write(jsPath + '\n')
                    self.jsFileNames.append(jsPath)
            print(Utils().tellTime() + "暴力JS文件提取成功，提取数量：" + str(len(self.jsFileNames)))
            self.getRealFilePath(self.jsFileNames, self.baseUrl, projectPath)

        else:
            print(Utils().tellTime() + "未提取到有效js路径，请进行人工审查！")

    def getRealFilePath(self, jsFileNames, jsUrlpath, projectPath):
        jsRealPaths = []
        base_url = Utils().getBaseUrl(jsUrlpath)
        for jsFileName in jsFileNames:
            jsFileName = base_url + jsFileName
            jsRealPaths.append(jsFileName)
        try:
            DownloadJs(self.jsFileNames, jsRealPaths, self.options, self.baseUrl).downloadJs(projectPath, False)
            print("DownloadJs功能正常")
        except Exception as e:
            print("[Err] %s" % e)

    def BruteForceStart(self, projectPath):
        print(Utils().tellTime() + "正在提取主页中存在的js代码...")
        for parent, dirnames, filenames in os.walk(projectPath + '/', followlinks=True):
            for filename in filenames:
                # 文件名和下载路径匹配来定位baseURL
                matchName = filename[7:]
                for path in self.originalPaths:
                    pathName = path[len(path) - len(matchName):]
                    if matchName == pathName:
                        self.baseUrl = path[0:len(path) - len(matchName)]
                        break
                filePath = os.path.join(parent, filename)
                self.checkCode(filePath, projectPath)
        print(Utils().tellTime() + "JS文件收集结束")
