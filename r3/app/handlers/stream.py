#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from uuid import uuid4
from ujson import dumps, loads
from datetime import datetime

import tornado.web
import tornado.gen

from r3.app.handlers import BaseHandler
from r3.app.utils import DATETIME_FORMAT

class StreamHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        arguments = self.request.arguments
        job_key = arguments['key'][0]
        job_id = uuid4()
        job_date = datetime.now()

        #mapper_input_queue = 'r3::jobs::%s::input' % job_key
        #self.redis.delete(mapper_input_queue)
        #return

        job_type_input_queue = 'r3::job-types::%s' % job_key
        self.redis.sadd(job_type_input_queue, str(job_id))

        start = time.time()
        input_stream = self.application.input_streams[job_key]
        items = input_stream.process(arguments)
        print "input stream took %.2f" % (time.time() - start)

        mapper_input_queue = 'r3::jobs::%s::input' % job_key
        mapper_output_queue = 'r3::jobs::%s::%s::output' % (job_key, job_id)
        mapper_error_queue = 'r3::jobs::%s::errors' % job_key

        with self.redis.pipeline() as pipe:
            start = time.time()

            for item in items:
                msg = {
                    'output_queue': mapper_output_queue,
                    'job_id': str(job_id),
                    'job_key': job_key,
                    'item': item,
                    'date': job_date.strftime(DATETIME_FORMAT),
                    'retries': 0
                }
                pipe.rpush(mapper_input_queue, dumps(msg))
            pipe.execute()
        print "input queue took %.2f" % (time.time() - start)

        start = time.time()
        results = []
        errored = False
        while (len(results) < len(items)):
            key, item = self.redis.blpop(mapper_output_queue)
            json_item = loads(item)
            if 'error' in json_item:
                json_item['retries'] -= 1
                self.redis.hset(mapper_error_queue, json_item['job_id'], dumps(json_item))
                errored = True
                break
            results.append(loads(json_item['result']))

        self.redis.delete(mapper_output_queue)
        print "map took %.2f" % (time.time() - start)

        try:
            if errored:
                self._error(500, 'Mapping failed. Check the error queue.')
            else:
                start = time.time()
                reducer = self.application.reducers[job_key]
                result = reducer.reduce(results)
                print "reduce took %.2f" % (time.time() - start)

                self.set_header('Content-Type', 'application/json')

                self.write(dumps(result))

                self.finish()
        finally:
            self.redis.srem(job_type_input_queue, str(job_id))

