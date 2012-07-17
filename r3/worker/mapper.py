#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import signal
import logging
import sys
import os
import argparse

import redis
from ujson import loads, dumps

from r3.app.utils import DATETIME_FORMAT, kls_import
from r3.app.keys import MAPPERS_KEY, JOB_TYPES_KEY, MAPPER_INPUT_KEY, MAPPER_WORKING_KEY, LAST_PING_KEY

class JobError(RuntimeError):
    pass

class CrashError(JobError):
    pass

class TimeoutError(JobError):
    pass

class Mapper:
    def __init__(self, job_type, mapper_key, redis_host, redis_port, redis_db, redis_pass):
        self.job_type = job_type
        self.mapper_key = mapper_key
        self.full_name = '%s::%s' % (self.job_type, self.mapper_key)
        self.timeout = None
        self.input_queue = MAPPER_INPUT_KEY % self.job_type
        self.working_queue = MAPPER_WORKING_KEY % self.full_name
        self.max_retries = 5

        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)

        logging.basicConfig(level=getattr(logging, 'WARNING'))
        self.initialize()
        logging.debug("Mapper UP - pid: %s" % os.getpid())
        logging.debug("Input Q: %s" % self.input_queue)
        logging.debug("Working Q: %s" % self.working_queue)

    def handle_signal(self, number, stack):
        self.unregister()
        sys.exit(number)

    def initialize(self):
        signal.signal(signal.SIGTERM, self.handle_signal)
        self.ping()

        item = self.redis.rpop(self.working_queue)
        if item:
            json_item = loads(item)
            json_item['retries'] += 1

            if json_item['retries'] > self.max_retries:
                json_item['error'] = '%s errored out after %d retries.' % (self.full_name, json_item['retries'])
                self.redis.rpush(json_item['output_queue'], dumps(json_item))
            else:
                item = dumps(json_item)
                self.map_item(item, json_item)

    def map(self):
        raise NotImplementedError()

    def run_block(self):
        try:
            while True:
                self.ping()
                logging.debug('waiting to process next item...')
                values = self.redis.brpop(self.input_queue, timeout=5)
                if values:
                    key, item = values
                    json_item = loads(item)
                    self.map_item(item, json_item)
        finally:
            self.unregister()

    def unregister(self):
        self.redis.srem(MAPPERS_KEY, self.full_name)
        self.redis.delete(LAST_PING_KEY % self.full_name)

    def ping(self):
        self.redis.delete(MAPPER_WORKING_KEY % self.full_name)
        self.redis.sadd(JOB_TYPES_KEY, self.job_type)
        self.redis.sadd(MAPPERS_KEY, self.full_name)
        self.redis.set(LAST_PING_KEY % self.full_name, datetime.now().strftime(DATETIME_FORMAT))

    def map_item(self, item, json_item):
        self.redis.set('r3::mappers::%s::working' % self.full_name, json_item['job_id'])
        self.redis.rpush(self.working_queue, item)
        result = dumps(self.map(json_item['item']))
        self.redis.rpush(json_item['output_queue'], dumps({
            'result': result
        }))
        self.redis.delete(self.working_queue)
        self.redis.delete('r3::mappers::%s::working' % self.full_name)

def main(arguments=None):
    if not arguments:
        arguments = sys.argv

    parser = argparse.ArgumentParser(description='runs the application that processes stream requests for r³')
    parser.add_argument('-l', '--loglevel', type=str, default='warning', help='the log level that r³ will run under')
    parser.add_argument('--redis-host', type=str, default='0.0.0.0', help='the ip that r³ will use to connect to redis')
    parser.add_argument('--redis-port', type=int, default=6379, help='the port that r³ will use to connect to redis')
    parser.add_argument('--redis-db', type=int, default=0, help='the database that r³ will use to connect to redis')
    parser.add_argument('--redis-pass', type=str, default='', help='the password that r³ will use to connect to redis')
    parser.add_argument('--mapper-key', type=str, help='the unique identifier for this mapper', required=True)
    parser.add_argument('--mapper-class', type=str, help='the fullname of the class that this mapper will run', required=True)

    args = parser.parse_args(arguments)

    if not args.mapper_key:
        raise RuntimeError('The --mapper_key argument is required.')

    logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

    try:
        klass = kls_import(args.mapper_class)
    except Exception, err:
        print "Could not import the specified %s class. Error: %s" % (args.mapper_class, err)
        raise

    mapper = klass(klass.job_type, args.mapper_key, redis_host=args.redis_host, redis_port=args.redis_port, redis_db=args.redis_db, redis_pass=args.redis_pass)
    try:
        mapper.run_block()
    except KeyboardInterrupt:
        print
        print "-- r³ mapper closed by user interruption --"


if __name__ == '__main__':
    main(sys.argv[1:])
