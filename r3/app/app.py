#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop

from r3.app.handlers.healthcheck import HealthcheckHandler
from r3.app.handlers.stream import StreamHandler

class R3ServiceApp(tornado.web.Application):

    def __init__(self, redis, log_level):
        self.redis = redis
        self.log_level = log_level

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
            (r'/stream/(?P<job_key>.+)/?', StreamHandler),
        ]

        self.redis.delete('r3::mappers')

        self.load_input_streams()
        self.load_reducers()

        super(R3ServiceApp, self).__init__(handlers)

    def load_input_streams(self):
        self.input_streams = {}

        stream = __import__('count_words_stream')

        self.input_streams['count-words'] = stream.CountWordsStream()

    def load_reducers(self):
        self.reducers = {}

        reducer = __import__('count_words_reducer')

        self.reducers['count-words'] = reducer.CountWordsReducer()


