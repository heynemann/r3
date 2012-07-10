#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2

def main():
    response = urllib2.urlopen('http://localhost:9999/stream')
    html = response.read()

if __name__ == '__main__':
    main()
