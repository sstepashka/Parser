#!/usr/bin/env python

import urllib, urllib2

class Proxies(object):
    """docstring for Proxies"""
    def __init__(self, filepath):
        super(Proxies, self).__init__()

        with open(filepath) as f:
            self.proxies = f.readlines()

        self.current = 0

    def next(self):
        try:
            proxy = self.proxies[self.current]
            self.current += 1
            return 'http://' + proxy + '/'
        except IndexError, e:
            return None
        except Exception, e:
            raise


class Parser(object):
    """docstring for Parser"""
    def __init__(self, proxies):
        super(Parser, self).__init__()
        self.proxies = proxies

    def parse(self, url):
        proxy = self.proxies.next()

        proxies = {'http': proxy}
        response = urllib.urlopen(url, proxies=proxies)
        print response.read()
        

def main():

    url = 'http://www.list-org.com/company/2100/show/founders'

    proxies = Proxies('proxies.txt')
    parser = Parser(proxies)

    parser.parse(url)

if __name__ == '__main__':
    main()