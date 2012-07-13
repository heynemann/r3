#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import signal
import logging
import sys
import os

import redis
from ujson import loads, dumps

from r3.app.utils import DATETIME_FORMAT

class JobError(RuntimeError):
    pass

class CrashError(JobError):
    pass

class TimeoutError(JobError):
    pass

class FastMapper:
    def __init__(self, key, redis_host, redis_port, redis_db, redis_pass):
        self.mappers_key = 'r3::mappers'
        self.job_types_key = 'r3::job-types'
        self.mapper_key = key
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)
        self.timeout = None
        self.initialize()
        print "MAPPER UP - PID: %s" % os.getpid()

    def initialize(self):
        pass

    def map(self):
        raise NotImplementedError()

    def run_block(self):
        while True:
            mapper_input_queue = 'r3::jobs::%s::input' % self.mapper_key

            key, item = self.redis.blpop(mapper_input_queue, timeout=0)

            item = loads(item)
            result = dumps(self.map(item['item']))
            self.redis.lpush(item['output_queue'], result)

class SafeMapper:
    def __init__(self, key, process_name, redis_host, redis_port, redis_db, redis_pass):
        self.mappers_key = 'r3::mappers'
        self.job_types_key = 'r3::job-types'
        self.mapper_key = key
        self.process_name = process_name
        self.full_name = '%s::%s' % (self.mapper_key, self.process_name)
        self.ping_key = 'r3::mappers::%s::last-ping'
        self.timeout = None
        self.input_queue = 'r3::jobs::%s::input' % self.mapper_key
        self.working_queue = 'r3::jobs::%s::working' % self.full_name
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

        item = self.redis.rpop(self.working_queue)
        if item:
            json_item = loads(item)
            json_item['retries'] += 1

            if json_item['retries'] > self.max_retries:
                json_item['error'] = '%s errored out after %d retries.' % (self.process_name, json_item['retries'])
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
        self.redis.srem(self.mappers_key, self.full_name)
        self.redis.delete(self.ping_key % self.full_name)

    def ping(self):
        self.redis.sadd(self.job_types_key, self.mapper_key)
        self.redis.sadd(self.mappers_key, self.full_name)
        self.redis.set(self.ping_key % self.full_name, datetime.now().strftime(DATETIME_FORMAT))

    def map_item(self, item, json_item):
        self.redis.set('r3::mappers::%s::working' % self.full_name, json_item['job_id'])
        self.redis.rpush(self.working_queue, item)
        result = dumps(self.map(json_item['item']))
        self.redis.rpush(json_item['output_queue'], dumps({
            'result': result
        }))
        self.redis.delete(self.working_queue)
        self.redis.delete('r3::mappers::%s::working' % self.full_name)

if __name__ == '__main__':
    mapper = SafeMapper("generic-mapper", redis_host=sys.argv[1], redis_port=int(sys.argv[2]), redis_db=0, redis_pass='r3')
    mapper.run_block()
