from urllib.parse import urlparse

import node_vm2
import os
import re

from DownloadJs import DownloadJs
from utils import Utils


class RecoverSpilt():

    def __init__(self, projectTag, baseUrl, options):
        self.name_list = []
        self.baseUrl = baseUrl
        self.jsFileNames = []
        self.localFileNames = []
        self.js_compile_results = []
        self.projectTag = projectTag
        self.options = options

    def jsCodeCompile(self, jsCode, projectPath):
        try:
            print(Utils().tellTime() + "正在处理异步加载代码中...")
            variable = re.findall(r'\[.*?\]', jsCode)
            if "[" and "]" in variable[0]:
                variable = variable[0].replace("[", "").replace("]", "")
            jsCodeFunc = "function js_compile(%s){js_url=" % (variable) + jsCode + "\nreturn js_url}"
            pattern_jscode = re.compile(r"\(\{\}\[(.*?)\]\|\|.\)", re.DOTALL)
            flag_code = pattern_jscode.findall(jsCodeFunc)
            if flag_code:
                jsCodeFunc = jsCodeFunc.replace("({}[%s]||%s)" % (flag_code[0], flag_code[0]), flag_code[0])
            pattern1 = re.compile(r"\{(.*?)\:")
            pattern2 = re.compile(r"\,(.*?)\:")
            nameList1 = pattern1.findall(jsCode)
            nameList2 = pattern2.findall(jsCode)
            nameList = nameList1 + nameList2
            nameList = list(set(nameList))
            with node_vm2.VM() as vm:
                vm.run(jsCodeFunc)
                for name in nameList:
                    if "\"" in name:
                        name = name.replace("\"", "")
                    if "undefined" not in vm.call("js_compile", name):
                        jsFileName = vm.call("js_compile", name)
                        self.jsFileNames.append(jsFileName)
            print(Utils().tellTime() + "异步JS文件提取成功，提取数量：" + str(len(self.jsFileNames)))
            path = projectPath[:-1] + "_result.txt"
            with open(path, "w+") as file:
                for jsPath1 in self.jsFileNames:
                    file.write(jsPath1 + '\n')
            self.getRealFilePath(self.jsFileNames, self.baseUrl, projectPath)
            print(Utils().tellTime() + "JsCodeCompile模块正常")
        except Exception as e:
            print("[Err] %s" % e)  # 这块有问题，逻辑要改进
            return 0

    def checkCodeSpilting(self, jsFilePath, projectPath):
        jsOpen = open(jsFilePath, 'r', encoding='UTF-8', errors="ignore")  # 防编码报错
        jsFile = jsOpen.readlines()
        jsOpen.close()
        jsFile = str(jsFile)  # 二次转换防报错
        if "document.createElement(\"script\");" in jsFile:
            print(Utils().tellTime() + "疑似存在JS异步加载：" + Utils().getFilename(jsFilePath))
            pattern = re.compile(r"\w\.p\+\"(.*?)\.js", re.DOTALL)
            if pattern:
                jsCodeList = pattern.findall(jsFile)
                for jsCode in jsCodeList:
                    if len(jsCode) < 300000: # js长度可能超过有效值（原值30k），扩大校验范围
                        jsCode = "\"" + jsCode + ".js\""
                        self.jsCodeCompile(jsCode, projectPath)

    def getRealFilePath(self, jsFileNames, jsUrlpath, projectPath):
        jsRealPaths = []
        base_url = Utils().getBaseUrl(jsUrlpath)
        for jsFileName in jsFileNames:
            # jsFileName = Utils().getFilename(jsFileName)  # 获取js名称
            jsFileName = base_url + jsFileName
            jsRealPaths.append(jsFileName)
        try:
            DownloadJs(self.jsFileNames, jsRealPaths, self.options, self.baseUrl).downloadJs(projectPath, False)
            print("DownloadJs功能正常")
        except Exception as e:
            print("[Err] %s" % e)

    def recoverStart(self, projectPath):
        for parent, dirnames, filenames in os.walk(projectPath + '/', followlinks=True):
            for filename in filenames:
                filePath = os.path.join(parent, filename)
                self.checkCodeSpilting(filePath, projectPath)
        print(Utils().tellTime() + "JS文件收集结束")
