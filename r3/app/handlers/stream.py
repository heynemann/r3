#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import logging
from uuid import uuid4
from ujson import dumps, loads
from datetime import datetime

import tornado.web
import tornado.gen

from r3.app.handlers import BaseHandler
from r3.app.utils import DATETIME_FORMAT
from r3.app.keys import PROCESSED, PROCESSED_FAILED, PROCESSED_SUCCESS, JOB_TYPE_KEY, MAPPER_INPUT_KEY, MAPPER_OUTPUT_KEY, MAPPER_ERROR_KEY

class StreamHandler(BaseHandler):
    def group_items(self, stream_items, group_size):
        items = []
        current_item = []
        items.append(current_item)
        for stream_item in stream_items:
            if len(current_item) == group_size:
                current_item = []
                items.append(current_item)
            current_item.append(stream_item)
        return items

    @tornado.web.asynchronous
    def get(self, job_key):
        arguments = self.request.arguments
        job_id = uuid4()
        job_date = datetime.now()

        job_type_input_queue = JOB_TYPE_KEY % job_key
        self.redis.sadd(job_type_input_queue, str(job_id))

        try:
            start = time.time()
            input_stream = self.application.input_streams[job_key]
            items = input_stream.process(arguments)
            if hasattr(input_stream, 'group_size'):
                items = self.group_items(items, input_stream.group_size)

            mapper_input_queue = MAPPER_INPUT_KEY % job_key
            mapper_output_queue = MAPPER_OUTPUT_KEY % (job_key, job_id)
            mapper_error_queue = MAPPER_ERROR_KEY % job_key

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
            logging.debug("input queue took %.2f" % (time.time() - start))

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
            logging.debug("map took %.2f" % (time.time() - start))

            if errored:
                self.redis.incr(PROCESSED)
                self.redis.incr(PROCESSED_FAILED)
                self._error(500, 'Mapping failed. Check the error queue.')
            else:
                start = time.time()
                reducer = self.application.reducers[job_key]
                result = reducer.reduce(results)
                logging.debug("reduce took %.2f" % (time.time() - start))

                self.set_header('Content-Type', 'application/json')

                self.write(dumps(result))

                self.redis.incr(PROCESSED)
                self.redis.incr(PROCESSED_SUCCESS)
 
                self.finish()
        finally:
            self.redis.srem(job_type_input_queue, str(job_id))

