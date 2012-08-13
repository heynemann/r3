#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
import argparse

import tornado.ioloop
from tornado.httpserver import HTTPServer
import redis

from r3.app.app import R3ServiceApp
from r3.app.config import Config


def main(arguments=None):
    '''Runs r³ server with the specified arguments.'''

    parser = argparse.ArgumentParser(description='runs the application that processes stream requests for r³')
    parser.add_argument('-b', '--bind', type=str, default='0.0.0.0', help='the ip that r³ will bind to')
    parser.add_argument('-p', '--port', type=int, default=9999, help='the port that r³ will bind to')
    parser.add_argument('-l', '--loglevel', type=str, default='warning', help='the log level that r³ will run under')
    parser.add_argument('-i', '--hide-index-page', action='store_true', default=False, help='indicates whether r³ app should show the help page')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='indicates whether r³ app should run in debug mode')
    parser.add_argument('--redis-host', type=str, default='0.0.0.0', help='the ip that r³ will use to connect to redis')
    parser.add_argument('--redis-port', type=int, default=6379, help='the port that r³ will use to connect to redis')
    parser.add_argument('--redis-db', type=int, default=0, help='the database that r³ will use to connect to redis')
    parser.add_argument('--redis-pass', type=str, default='', help='the password that r³ will use to connect to redis')
    parser.add_argument('-c', '--config-file', type=str, help='the config file that r³ will use to load input stream classes and reducers', required=True)

    args = parser.parse_args(arguments)

    cfg = Config(args.config_file)

    c = redis.StrictRedis(host=args.redis_host, port=args.redis_port, db=args.redis_db, password=args.redis_pass)

    logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

    application = R3ServiceApp(redis=c, config=cfg, log_level=args.loglevel.upper(), debug=args.debug, show_index_page=not args.hide_index_page)

    server = HTTPServer(application)
    server.bind(args.port, args.bind)
    server.start(1)

    try:
        logging.debug('r³ service app running at %s:%d' % (args.bind, args.port))
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print "-- r³ service app closed by user interruption --"

if __name__ == "__main__":
    main(sys.argv[1:])
