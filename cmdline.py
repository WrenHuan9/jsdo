import optparse
import sys

KITTY_BANNER = '''
  _         _                      _                       _     
 | |__     | |    __ _     __     | |__    __     __ _    | |_   
 | '_ \    | |   / _` |   / _|    | / /   / _|   / _` |   |  _|  
 |_.__/   _|_|_  \__,_|   \__|_   |_\_\   \__|_  \__,_|   _\__|  
_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| 
"`-F-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-C-' 
'''

class CommandLines():

    def cmd(self):
        parse = optparse.OptionParser()
        parse.add_option('-u', '--url', dest='url', help='Please Enter the Target Site')
        parse.add_option('-p', '--proxy', dest='proxy', type=str, help='Please Enter your own Proxy Address')
        parse.add_option('-f', '--flag', dest='ssl_flag', default='0', type=str, help='SSL SEC FLAG')
        (options, args) = parse.parse_args()
        print(KITTY_BANNER)
        if options.url is None:
            parse.print_help()
            sys.exit(0)
        return options