#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import time
from datetime import datetime
import sys
import os

import redis
from ujson import loads, dumps

from r3.app.utils import logger

class JobError(RuntimeError):
    pass

class CrashError(JobError):
    pass

class TimeoutError(JobError):
    pass

class FastMapper:
    def __init__(self, key, redis_host, redis_port, redis_db, redis_pass):
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
        self.mapper_key = key
        self.process_name = process_name
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)
        self.timeout = None
        self.input_queue = 'r3::jobs::%s::input' % self.mapper_key
        self.working_queue = 'r3::jobs::%s::%s::working' % (self.mapper_key, self.process_name)
        self.max_retries = 5

        self.initialize()
        print "Mapper UP - pid: %s" % os.getpid()
        print "Input Q: %s" % self.input_queue
        print "Working Q: %s" % self.working_queue

    def initialize(self):
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
        while True:
            key, item = self.redis.brpop(self.input_queue, timeout=0)
            json_item = loads(item)
            self.map_item(item, json_item)

    def map_item(self, item, json_item):
        self.redis.rpush(self.working_queue, item)
        result = dumps(self.map(json_item['item']))
        self.redis.rpush(json_item['output_queue'], dumps({
            'result': result
        }))
        self.redis.delete(self.working_queue)


class ForkMapper:
    def __init__(self, key, redis_host, redis_port, redis_db, redis_pass):
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

            #print "waiting for item..."
            key, item = self.redis.blpop(mapper_input_queue, timeout=0)
            #print item

            item = loads(item)
            self.child = os.fork()
            if self.child:
                try:
                    start = datetime.now()

                    # waits for the result or times out
                    while True:
                        pid, status = os.waitpid(self.child, os.WNOHANG)
                        if pid != 0:
                            if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
                                break
                            if os.WIFSTOPPED(status):
                                logger.warning("Process stopped by signal %d" % os.WSTOPSIG(status))
                            else:
                                if os.WIFSIGNALED(status):
                                    raise CrashError("Unexpected exit by signal %d" % os.WTERMSIG(status))
                                raise CrashError("Unexpected exit status %d" % os.WEXITSTATUS(status))

                        time.sleep(0.0005)

                        now = datetime.now()
                        if self.timeout and ((now - start).seconds > self.timeout):
                            os.kill(self.child, signal.SIGKILL)
                            os.waitpid(-1, os.WNOHANG)
                            raise TimeoutError("Timed out after %d seconds" % self.timeout)

                except OSError as ose:
                    import errno

                    if ose.errno != errno.EINTR:
                        raise ose
                except JobError, e:
                    logger.error(str(e))

            else:
                result = dumps(self.map(item['item']))
                self.redis.lpush(item['output_queue'], result)
                os._exit(0)


if __name__ == '__main__':
    mapper = Mapper("generic-mapper", redis_host=sys.argv[1], redis_port=int(sys.argv[2]), redis_db=0, redis_pass='r3')
    mapper.run_block()
