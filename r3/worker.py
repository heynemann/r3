#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis

def main():
    client = redis.Redis(host='localhost', port=7778, db=0, password="r3")
    pubsub = client.pubsub()

    pubsub.subscribe(['some-event'])

    while True:
        print "waiting for next item..."
        result = pubsub.listen().next()
        print result

if __name__ == '__main__':
    main()
