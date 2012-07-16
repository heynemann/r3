#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from os.path import abspath, isabs, join
import logging
import argparse

from r3.web.app import app
from r3.web.extensions import RedisDB

def main(arguments=None):
    '''Runs r³ web app with the specified arguments.'''

    parser = argparse.ArgumentParser(description='runs the web admin that helps in monitoring r³ usage')
    parser.add_argument('-b', '--bind', type=str, default='0.0.0.0', help='the ip that r³ will bind to')
    parser.add_argument('-p', '--port', type=int, default=8888, help='the port that r³ will bind to')
    parser.add_argument('-l', '--loglevel', type=str, default='warning', help='the log level that r³ will run under')
    parser.add_argument('--redis-host', type=str, default='0.0.0.0', help='the ip that r³ will use to connect to redis')
    parser.add_argument('--redis-port', type=int, default=6379, help='the port that r³ will use to connect to redis')
    parser.add_argument('--redis-db', type=int, default=0, help='the database that r³ will use to connect to redis')
    parser.add_argument('--redis-pass', type=str, default='', help='the password that r³ will use to connect to redis')
    parser.add_argument('-c', '--config-file', type=str, default='', help='the configuration file that r³ will use')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help='indicates that r³ will be run in debug mode')

    args = parser.parse_args(arguments)

    logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

    if args.config_file:
        config_path = args.config_file
        if not isabs(args.config_file):
            config_path = abspath(join(os.curdir, args.config_file))

        app.config.from_pyfile(config_path, silent=False)
    else:
        app.config.from_object('r3.web.config')

    app.db = RedisDB(app)
    try:
        logging.debug('r³ web app running at %s:%d' % (args.bind, args.port))
        app.run(debug=args.debug, host=app.config['WEB_HOST'], port=app.config['WEB_PORT'])
    except KeyboardInterrupt:
        print
        print "-- r³ web app closed by user interruption --"

if __name__ == "__main__":
    main(sys.argv[1:])
