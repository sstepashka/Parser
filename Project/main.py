#!/usr/bin/env python

import urllib, urllib2
from lxml import etree, html
import re
import os.path
from antigate import AntiGate


ANTIGATE_KEY = 'a2abe6583c0e14299c36ba3720201520'


class NotFoundFoundersException(Exception):
    pass


class CaptchaException(Exception):
    pass


class Proxies(object):
    """docstring for Proxies"""
    def __init__(self, filepath):
        super(Proxies, self).__init__()

        with open(filepath) as f:
            self.proxies = f.read().splitlines() 

        self.current = 0

    def next(self):
        try:
            proxy = self.proxies[self.current]
            self.current += 1
            return 'http://' + proxy + '/'
        except IndexError, e:
            self.current = 1
            return self.proxies[0]
        except Exception, e:
            raise


class Parser(object):
    """docstring for Parser"""
    def __init__(self, proxies):
        super(Parser, self).__init__()
        self.proxies = proxies

        self.companies = []

    def add(self, url):
        self.companies.append(url)

    def pop(self):
        try:
            companyID = self.companies[0]
            del self.companies[0]
            return companyID
        except IndexError, e:
            return None
        except Exception, e:
            raise

    def loadCompanyDataOrCache(self, companyID, proxy):
        cache_path = "cache/%s.html" % (companyID)

        data = None

        if os.path.isfile(cache_path):
            print "Load company %s from cache" % companyID
            with open(cache_path, "r") as cache:
                data = cache.read()
        else:
            # {"http":proxy}
            # proxy_support = urllib2.ProxyHandler()
            # opener = urllib2.build_opener(proxy_support)
            # urllib2.install_opener(opener)

            url = "http://www.list-org.com/company/%s/show/founders" % (companyID)
            print "URL: " + url

            data = urllib2.urlopen(url).read()

            if len(self.grepFounders(data)):
                print "Save company %s to cache: %s" % (companyID, cache_path)
                with open(cache_path, "w") as cache:
                    cache.write(data)

        return data

    def parseCompany(self, companyID):
        proxy = self.proxies.next()

        print "Using proxy: " + proxy

        data = self.loadCompanyDataOrCache(companyID, proxy)

        founders = self.grepFounders(data)

        if founders and len(founders):
            for founder in founders:
                self.add(founder)
            
            print "Found %i founders" % len(founders)
        else:
            raise NotFoundFoundersException

    def grepFounders(self, htmlText):
        tree = html.fromstring(htmlText)
        elements = tree.xpath('//table[@class="tt f08"]/tr/td[2]/a/@href')

        return list(map(lambda element: re.split(r'[\\/]', element)[-1], elements))

    def parse(self):
        companyID = self.pop()
        while companyID:
            connect = False

            while not connect:
                try:
                    self.parseCompany(companyID)
                    connect = True
                except IOError, e:
                    print "Connection Error, next proxy using"
                    connect = False
                except NotFoundFoundersException, e:
                    print "Not found founders, maybe captcha"
                    self.captcha(companyID)
                    connect = False
                except Exception, e:
                    raise

            companyID = self.pop()

    def captcha(self, companyID):
        captcha_url = 'http://www.list-org.com/bot.php'

        url = "http://www.list-org.com/company/%s/show/founders" % (companyID)

        opener = urllib2.build_opener()
        urllib2.install_opener(opener)

        data = urllib2.urlopen(url).read()

        tree = html.fromstring(data)
        elements = tree.xpath('//div[@class="content"]/form/img/@src')

        if len(elements) > 0:
            #captcha
            captcha_data = urllib2.urlopen(elements[0]).read()
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print elements[0]
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        else:
            #ignore
            pass

        

def main():
    # How to Use AntiGate
    # gate = AntiGate(ANTIGATE_KEY, 'captcha.gif')
    # print gate

    proxies = Proxies('proxies.txt')
    parser = Parser(proxies)

    companyID = '2100'

    parser.add(companyID)

    parser.parse()

if __name__ == '__main__':
    main()