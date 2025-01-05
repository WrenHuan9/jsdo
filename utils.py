import os
import random
import shutil
import time
from urllib.parse import urlparse


class Utils():

    def creatTag(self, num):  # 生成随机tag
        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt

    def getFilename(self, url):
        filename = url.split('/')[-1]
        filename = filename.split('?')[0]
        return filename

    def creatSometing(self, choice, path):  # choice1文件夹，2文件
        # 返回0已经存在，返回1创建文件夹成功，返回2创建文件夹失败
        if choice == 1:
            path = path.split('/')  # 输入统一用 /
            path = os.sep.join(path)
            path = os.getcwd() + os.sep + path
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                    return 1
            except:
                return 2
            return 0
        if choice == 2:
            path = path.split('/')
            del path[-1]
            path = os.sep.join(path)  #
            path = os.getcwd() + os.sep + path
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                    return 1
            except:
                return 2
            return 0

    def getMiddleStr(self, content, startStr, endStr):  # 获取中间字符串通用函数
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex:endIndex]

    def tellTime(self):  # 时间输出
        localtime = "[" + str(time.strftime('%H:%M:%S', time.localtime(time.time()))) + "] "
        return localtime

    def getMD5(self, file_path):
        files_md5 = os.popen('md5 %s' % file_path).read().strip()
        file_md5 = files_md5.replace('MD5 (%s) = ' % file_path, '')
        return file_md5

    def copyPath(self, path, out):
        out = out + os.sep + path.split(os.sep)[-1]
        os.mkdir(out)
        for files in os.listdir(path):
            name = os.path.join(path, files)
            back_name = os.path.join(out, files)
            if os.path.isfile(name):
                if os.path.isfile(back_name):
                    if self.getMD5(name) != self.getMD5(back_name):
                        shutil.copy(name, back_name)
                else:
                    shutil.copy(name, back_name)
            else:
                if not os.path.isdir(back_name):
                    os.makedirs(back_name)
                self.main(name, back_name)

    def generateFullPath(self, js_paths, baseUrl, res):
        jsFullPaths = []
        for jsPath in js_paths:  # 路径处理多种情况./ ../ / http
            if jsPath[:2] == "./":
                jsPath = jsPath.replace("./", "")
                jsRealPath = baseUrl + jsPath
                jsFullPaths.append(jsRealPath)
            elif jsPath[:3] == "../":
                tmpPath = res.path.split('/')
                if res.path[-1] != "/":
                    tmpPath = res.path + "/"
                    tmpPath = tmpPath.split('/')
                new_tmpPath = tmpPath[:]  # 防止解析报错
                dirCount = jsPath.count('../') + 1
                tmpCount = 1
                jsPath = jsPath.replace("../", "")
                while tmpCount <= dirCount:
                    del new_tmpPath[-1]
                    tmpCount = tmpCount + 1
                baseUrl = res.scheme + "://" + res.netloc + "/".join(new_tmpPath) + "/"
                jsRealPath = baseUrl + jsPath
                jsFullPaths.append(jsRealPath)
            elif jsPath[:2] == "//":  # 自适应域名js
                jsRealPath = res.scheme + ":" + jsPath
                jsFullPaths.append(jsRealPath)
            elif jsPath[:1] == "/":
                jsRealPath = res.scheme + "://" + res.netloc + jsPath
                jsFullPaths.append(jsRealPath)
            elif jsPath[:4] == "http":
                jsRealPath = jsPath
                jsFullPaths.append(jsRealPath)
            else:
                jsRealPath = baseUrl + jsPath
                jsFullPaths.append(jsRealPath)
        return jsFullPaths

    def getBaseUrl(self, path):
        res = urlparse(path)
        if res.path == "":
            baseUrl = res.scheme + "://" + res.netloc + "/"
        else:
            baseUrl = res.scheme + "://" + res.netloc + res.path
            if res.path[-1:] != "/":  # 文件夹没"/",若输入的是文件也会被加上，但是影响不大
                baseUrl = baseUrl + "/"
        if path[-1:] != "/":  # 有文件的url
            tmpPath = res.path.split('/')
            tmpPath = tmpPath[:]  # 防止解析报错
            del tmpPath[-1]
            baseUrl = res.scheme + "://" + res.netloc + "/".join(tmpPath) + "/"
        return baseUrl