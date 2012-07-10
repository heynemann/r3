#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis

def main():
    client = redis.StrictRedis(host='localhost', port=7778, db=0, password="r3")
    client.publish('some-event', 'some-data')

if __name__ == '__main__':
    main()

