import json
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

    def jsCodeCompileWithNormalMode(self, jsCode, projectPath):
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
        except Exception as e:
            print("[Err] %s" % e)  # 这块有问题，逻辑要改进
            return 0

    def jsCodeCompileWithNewMode(self, jsCode, public_path, projectPath):
        """
            Extracts chunk URLs from the new webpack pattern.
            project_path_base_url is the base URL if publicPath is relative.
            """
        print(Utils().tellTime() + "正在处理新型异步加载代码...")

        if not public_path.endswith('/'):
            public_path += '/'

        # 处理路径
        if (public_path == "/" or public_path == "" or public_path.startswith("./")) and self.baseUrl:
            # 假设 project_path_base_url 已经是完整的 URL 前缀
            base_url = self.baseUrl
            if not base_url.endswith('/'):
                base_url += '/'
            # 如果 public_path 不是 "/" 或空, 则需要拼接
            if public_path != "/" and public_path != "":
                effective_public_path = public_path.lstrip('./')
                final_url_prefix = base_url + effective_public_path
            else:
                final_url_prefix = base_url  # public_path 是 "/" 或 "" 时，直接用 base_url
        elif public_path.startswith("http"):  # public_path 是绝对 URL
            final_url_prefix = public_path
        elif self.baseUrl:  # public_path 是绝对路径但不是完整URL (例如 /js/)
            cleaned_base = self.baseUrl.rstrip('/')
            cleaned_public = public_path.lstrip('/')
            final_url_prefix = f"{cleaned_base}/{cleaned_public}"
            if not final_url_prefix.endswith('/'):  # 确保末尾有斜杠
                final_url_prefix += '/'
        else:  # 无法确定绝对路径，直接使用提取到的 public_path
            final_url_prefix = public_path
            if not final_url_prefix:  # 如果 public_path 为空
                final_url_prefix = "/"  # 默认为根相对路径

        pattern_new_chunks = re.compile(
            r'script\.src\s*=\s*__webpack_require__\.p\s*\+\s*""\s*\+\s*chunkId\s*\+\s*"(.*?)"\s*\+\s*(\{[\s\S]*?\})\[chunkId\]'
        )

        match = pattern_new_chunks.search(jsCode)

        if not match:
            print(Utils().tellTime() + "未找到新型 chunk 模式。")
            return []

        filename_suffix_part = match.group(1)
        chunk_map_string = match.group(2)

        try:
            chunk_map = json.loads(chunk_map_string)
        except json.JSONDecodeError as e:
            print(f"{Utils().tellTime()} 解析 chunk map 失败: {e}")
            print(f"Map string: {chunk_map_string[:200]}...")  # 打印部分 map 字符串以供调试
            return []

        for chunk_id_key, hash_value in chunk_map.items():
            self.jsFileNames.append(f"{chunk_id_key}{filename_suffix_part}{hash_value}")

        print(Utils().tellTime() + "新模式异步JS文件提取成功，提取数量：" + str(len(self.jsFileNames)))
        path = projectPath[:-1] + "_result.txt"
        with open(path, "w+") as file:
            for jsPath1 in self.jsFileNames:
                file.write(jsPath1 + '\n')
        self.getRealFilePath(self.jsFileNames, final_url_prefix, projectPath)

    def extract_public_path(self, js_content):
        """
        Extracts the publicPath (e.g., __webpack_require__.p or u.p)
        """
        match = re.search(r'(?:__webpack_require__\.p|u\.p)\s*=\s*"([^"]*)"', js_content)
        if match:
            return match.group(1)
        print(Utils().tellTime() + "Warning: publicPath not explicitly found, defaulting to '/'")
        return "/"

    def checkCodeSpilting(self, jsFilePath, projectPath):
        jsOpen = open(jsFilePath, 'r', encoding='UTF-8', errors="ignore")  # 防编码报错
        jsFile = jsOpen.readlines()
        jsOpen.close()
        jsFile = str(jsFile)  # 二次转换防报错
        mode = int(self.options.mode)
        if mode == 1:
            public_path = self.extract_public_path(jsFile)
            self.jsCodeCompileWithNewMode(jsFile, public_path, projectPath)
        else:
            if "document.createElement(\"script\");" in jsFile:
                print(Utils().tellTime() + "疑似存在JS异步加载：" + Utils().getFilename(jsFilePath))
                pattern = re.compile(r"\w\.p\+\"(.*?)\.js", re.DOTALL)
                jsCodeList = pattern.findall(jsFile)
                for jsCode in jsCodeList:
                    if len(jsCode) < 300000: # js长度可能超过有效值（原值30k），扩大校验范围
                        jsCode = "\"" + jsCode + ".js\""
                        self.jsCodeCompileWithNormalMode(jsCode, projectPath)

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
