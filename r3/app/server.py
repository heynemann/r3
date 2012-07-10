#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging

import tornado.ioloop
from tornado.httpserver import HTTPServer

from r3.app.app import R3ServiceApp


def main(arguments=None):
    '''Runs r³ server with the specified arguments.'''
    log_level = 'debug'
    port = int(arguments[1])
    ip = arguments[0]

    #log_level = arguments['log_level']
    #port = arguments['port']
    #ip = arguments['ip']

    logging.basicConfig(level=getattr(logging, log_level.upper()))

    application = R3ServiceApp(log_level)

    server = HTTPServer(application)
    server.bind(port, ip)
    server.start(1)

    try:
        logging.debug('r³ service app running at %s:%d' % (ip, port))
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print "-- r³ service app closed by user interruption --"

if __name__ == "__main__":
    main(sys.argv[1:])
