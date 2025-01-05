import os
from configparser import ConfigParser
from configparser import RawConfigParser


class ReadConfig(object):

    def __init__(self):
        self.path = os.getcwd() + os.sep + "config.ini"  # 配置文件地址
        self.config = ConfigParser()
        self.rawconfig = RawConfigParser()
        self.res = []
        self.customRes = []

    def getValue(self, sections, key):
        self.config.read(self.path, encoding="utf-8")
        options = self.config[sections][key]
        self.res.append(options)
        return self.res

    def getCustomValue(self, workDir, sections, key):
        self.rawconfig.read(workDir, encoding="utf-8")
        options = self.rawconfig[sections][key]
        self.customRes.append(options)
        return self.customRes