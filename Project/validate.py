#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import ntpath
import re

def main():
    product_files = glob.glob("./cache/*.html")

    names = []

    for i in product_files:
        basename = ntpath.basename(i)
        name, extension = re.search(r'^(?P<name>.*)\.(?P<ext>.*)$', basename).groups()
        names.append(name)
    with open('companies.txt', 'r') as f:
        lines = [line.strip() for line in f.readlines() if line]

        for line in lines:
            if not line in names:
                print line 
                raise

if __name__ == '__main__':
    main()