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

class Mapper:
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
