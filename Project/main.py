#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2
from lxml import etree, html
import re
import os.path
from antigate import AntiGate
from priority_queue import PriorityQueue
import time

ANTIGATE_KEY = 'a2abe6583c0e14299c36ba3720201520'

CAPTCHA_URL = 'http://www.list-org.com/bot.php'

LAST_COOKIE = None


class NotFoundFoundersException(Exception):
    pass


class CaptchaException(Exception):
    def __init__(self, response):
        self.response = response


class NotFoundCaptcha(Exception):
    pass


class JobEnd(Exception):
    pass


class NoRedirection(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response


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

        self.companies = PriorityQueue()

        self.parsed = set()

    def add(self, url, priority = 1.):
        if not url in self.parsed:
            self.companies.push(url, priority)

    def pop(self):
        try:
            companyID = self.companies.pop()

            while not companyID:
                companyID = self.companies.pop()

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
            # proxy_support = urllib2.ProxyHandler({"http":proxy})
            opener = urllib2.build_opener(NoRedirection)
            urllib2.install_opener(opener)

            url = "http://www.list-org.com/company/%s/show/founders" % (companyID)
            print "URL: " + url

            response = urllib2.urlopen(url)
            status_code = response.getcode()

            LAST_COOKIE = response.info().getheader('Set-Cookie')
            opener = urllib2.build_opener(NoRedirection)
            opener.addheaders.append(('Cookie', LAST_COOKIE))
            urllib2.install_opener(opener)
            r = urllib2.urlopen('http://www.list-org.com/js/org.js')
            # time.sleep(1)

            if status_code == 200:
                data = response.read()

                print "Save company %s to cache: %s" % (companyID, cache_path)
                with open(cache_path, "w") as cache:
                    cache.write(data)

            elif status_code == 307 and response.info().getheader('Location') == CAPTCHA_URL:
                raise CaptchaException(response)
            else:
                pass

        return data

    def parseCompany(self, companyID):
        self.parsed.add(companyID)

        proxy = self.proxies.next()

        print "Using proxy: " + proxy

        data = self.loadCompanyDataOrCache(companyID, proxy)

        #if len(self.parsed) > 1000:
        #    raise JobEnd()

        founders = self.grepFounders(data)

        if founders and len(founders):
            for founder in founders:
                self.add(founder['companyID'], founder['priority'])
            
            print "Found %i founders" % len(founders)
        else:
            raise NotFoundFoundersException

    def grepFounders(self, htmlText):
        tree = html.fromstring(htmlText)
        elements = tree.xpath('//table[@class="tt f08"]/tr')

        result = []

        for element in elements[1:-1]:
            link1 = element.xpath('td[2]/a/@href')
            if len(link1) > 0:
                link = link1[0]
                percent = float(element.xpath('td[3]/text()')[0][:-1])

                if percent <= 0.:
                    percent = 0.1

                company_sum = self.parseSum(element.xpath('td[4]/text()')[0])

                priority = company_sum / percent
                company_identifier = re.split(r'[\\/]', link)[-1]

                result.append(
                        {
                        'companyID': company_identifier,
                        'priority': priority,
                        }
                    )

        return result

    def parseSum(self, sum_string):
        res = sum_string.split(' ')

        factor = 1.

        if res[-1] == u'млн.руб.':
            factor = 1000.

        return float(res[0]) * factor

    def parse(self):
        companyID = self.pop()
        end = False
        while companyID and not end:
            connect = False

            while not connect and not end:
                try:
                    self.parseCompany(companyID)
                    connect = True
                except IOError, e:
                    print "Connection Error, next proxy using"
                    connect = False
                except NotFoundFoundersException, e:
                    print "Not found founders, maybe captcha"
                    connect = True
                except CaptchaException, e:
                    self.captcha(e.response)
                    connect = False

                except JobEnd, e:
                    end = True
                    print 'Job End !!!'
                except Exception, e:
                    raise

            companyID = self.pop()
            #time.sleep(15)

        print companyID

    def captcha(self, response):
        captcha_url = 'http://www.list-org.com/bot.php'

        cookie = response.info().getheader('Set-Cookie')

        opener = urllib2.build_opener(NoRedirection)
        opener.addheaders.append(('Cookie', cookie))
        urllib2.install_opener(opener)

        captcha_response = urllib2.urlopen(captcha_url)
        data = captcha_response.read()

        tree = html.fromstring(data)
        elements = tree.xpath('//div[@class="content"]/form/img/@src')

        print data
        print response.info()

        if len(elements) > 0:
            image_url = elements[0]
            captcha_data = urllib2.urlopen(image_url).read()
			
            print image_url

            with open('captcha.gif', "wb") as myfile:
                    myfile.write(captcha_data)
                    myfile.close()
            
            config = {
                    'is_russian': '1',
                }
            gate = None
            while not gate:
                try:
                    gate = AntiGate(ANTIGATE_KEY, 'captcha.gif', send_config=config)
                    gate = gate.lower()
                except Exception, e:
                    print e
            # gate = raw_input()

            file_path = 'captcha/' + str(gate) + '.gif'

            with open(file_path, "wb") as myfile:
                    myfile.write(captcha_data)

            values = {
                    'keystring' : str(gate),
                    'submit' : " Проверить! ",
                    }

            opener = urllib2.build_opener()
            opener.addheaders.append(('Cookie', cookie))
            urllib2.install_opener(opener)

            data = urllib.urlencode(values)
            req = urllib2.Request(captcha_url, data)
            req.get_method = lambda: 'POST'

            try:
                response = urllib2.urlopen(req)
                the_page = response.read()
                print the_page
            except urllib2.HTTPError, e:
                contents = e.read()
                print contents
            except Exception, e:
                raise

        else:
            raise NotFoundCaptcha

        

def main():
    proxies = Proxies('proxies.txt')
    parser = Parser(proxies)

    companyID = '2100'

    parser.add(companyID)

    parser.parse()

if __name__ == '__main__':
    main()