from Controller import Project
from cmdline import CommandLines


class Program():
    def __init__(self, options):
        self.options = options

    def check(self):
        url = self.options.url
        t = Project(url, self.options)
        t.start()


if __name__ == '__main__':
    cmd = CommandLines().cmd()
    JsDownload = Program(cmd)
    JsDownload.check()