#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from uuid import uuid4
from ujson import dumps, loads

import tornado.web
import tornado.gen

from r3.app.handlers import BaseHandler

class StreamHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        arguments = self.request.arguments
        job_key = arguments['key'][0]
        job_id = uuid4()

        #mapper_input_queue = 'r3::jobs::%s::input' % job_key
        #self.redis.delete(mapper_input_queue)
        #return
 
        start = time.time()
        input_stream = self.application.input_streams[job_key]
        items = input_stream.process(arguments)
        print "input stream took %.2f" % (time.time() - start)

        mapper_input_queue = 'r3::jobs::%s::input' % job_key
        mapper_output_queue = 'r3::jobs::%s::%s::output' % (job_key, job_id)

        start = time.time()
        for item in items:
            msg = {
                'output_queue': mapper_output_queue,
                'job_id': str(job_id),
                'job_key': job_key,
                'item': item
            }
            yield tornado.gen.Task(self.redis.rpush, mapper_input_queue, dumps(msg))

        #pipe = self.redis.pipeline()
        #results = []
        #for i in range(len(items)):
            #result = yield tornado.gen.Task(self.redis.blpop, mapper_output_queue)
            #results.append(loads(result))
            #pipe.blpop(mapper_output_queue)
        #results = yield tornado.gen.Task(pipe.execute)
        #results = [loads(item) for item in results if item is not None]
        #print len(results)
        #print len(items)

        results = []
        #mapped_items = yield tornado.gen.Task(self.redis.llen, mapper_output_queue)
        def wtf(item):
            import ipdb;ipdb.set_trace()

        #while (len(results) < len(items)):
            #print "%d < %d" % (len(results), len(items))
        self.redis.blpop(mapper_output_queue, callback=wtf)
            #item = loads(item)
            #results.append(item)

        #print "map took %.2f" % (time.time() - start)

        #start = time.time()
        #reducer = self.application.reducers[job_key]
        #result = reducer.reduce(results)
        #print "reduce took %.2f" % (time.time() - start)

        #self.set_header('Content-Type', 'application/json')

        #self.write(dumps(result))

        #self.finish()

