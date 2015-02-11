#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2
from lxml import etree, html

class NoRedirection(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response

def main():
    cookie = 'PHPSESSID=rsma79v3envsvdul6r4nqsa026'

    captcha_url = 'http://www.list-org.com/bot.php'

    opener = urllib2.build_opener(NoRedirection)
    opener.addheaders.append(('Cookie', cookie))

    urllib2.install_opener(opener)

    captcha_response = urllib2.urlopen(captcha_url)
    data = captcha_response.read()

    tree = html.fromstring(data)
    elements = tree.xpath('//div[@class="content"]/form/img/@src')

    captcha_data = urllib2.urlopen(elements[0]).read()

    with open('captcha.gif', "w") as myfile:
            myfile.write(captcha_data)

    res = raw_input()

    values = {
            'keystring' : str(res),
            'submit' : " Проверить! ",
            }

    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', cookie))
    urllib2.install_opener(opener)

    data = urllib.urlencode(values)

    req = urllib2.Request(captcha_url, data)
    req.get_method = lambda: 'POST'

    response = urllib2.urlopen(req)
    the_page = response.read()

    print response.info()

    pass

if __name__ == '__main__':
    main()