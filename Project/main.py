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

        self.urls = []

    def add(self, url):
        self.urls.append(url)

    def pop(self):
        try:
            url = self.urls[0]
            del self.urls[0]
            return url
        except IndexError, e:
            return None
        except Exception, e:
            raise

    def parse(self, url):
        proxy = self.proxies.next()

        if not proxy is None:
            proxies = {'http': proxy}
            response = urllib.urlopen(url, proxies=proxies)
            data = response.read()

    def parse(self):
        url = self.pop()
        if not url is None:
            self.parse(url)
        

def main():

    url = 'http://www.list-org.com/company/2100/show/founders'

    proxies = Proxies('proxies.txt')
    parser = Parser(proxies)

    parser.add(url)

    parser.parse()

if __name__ == '__main__':
    main()