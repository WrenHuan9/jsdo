import optparse
import sys


class CommandLines():

    def cmd(self):
        parse = optparse.OptionParser()
        parse.add_option('-u', '--url', dest='url', help='Please Enter the Target Site')
        parse.add_option('-p', '--proxy', dest='proxy', type=str, help='Please Enter your own Proxy Address')
        parse.add_option('-f', '--flag', dest='ssl_flag', default='0', type=str, help='SSL SEC FLAG')
        (options, args) = parse.parse_args()
        if options.url is None:
            parse.print_help()
            sys.exit(0)
        return options