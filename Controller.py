import os
import shutil
import sys

from urllib.parse import urlparse

from CheckPacker import CheckPacker
from Parse import ParseMainPage
import ReadConfig
from Recoverspilt import RecoverSpilt
from utils import Utils

class Project():

    def __init__(self, url, options):
        self.url = url
        self.codes = {}
        self.options = options
        self.projectTag = Utils().creatTag(6)

    def start(self):
        res = urlparse(self.url)
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_")
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        projectPath = "tmp" + os.sep + self.projectTag + "_" + domain
        os.mkdir(projectPath)
        projectPath = projectPath + os.sep
        try:
            baseUrl = ParseMainPage(self.projectTag, projectPath, self.url, self.options).parseMainPageStart()
            checkResult = CheckPacker(self.projectTag, self.url, self.options).checkStart(os.path.abspath(projectPath))
            if checkResult == 1 or checkResult == 777:
                if checkResult != 777:
                    print("[!] " + "恭喜，这个站点很可能是通过前端打包器构建的！")
                RecoverSpilt(self.projectTag, baseUrl, self.options).recoverStart(os.path.abspath(projectPath)+os.sep)
            else:
                print("[!] " + "未检测到前端打包器特征")
        finally:
            shutil.rmtree(projectPath)
