#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop

from r3.app.handlers.healthcheck import HealthcheckHandler
from r3.app.handlers.stream import StreamHandler
from r3.app.handlers.index import IndexHandler
from r3.app.utils import kls_import

class R3ServiceApp(tornado.web.Application):

    def __init__(self, redis, config, log_level, debug, show_index_page):
        self.redis = redis
        self.log_level = log_level
        self.config = config
        self.debug = debug

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
        ]

        if show_index_page:
            handlers.append(
                (r'/', IndexHandler)
            )

        handlers.append(
            (r'/stream/(?P<job_key>.+)/?', StreamHandler),
        )

        self.redis.delete('r3::mappers')

        self.load_input_streams()
        self.load_reducers()

        super(R3ServiceApp, self).__init__(handlers, debug=debug)

    def load_input_streams(self):
        self.input_streams = {}

        if hasattr(self.config, 'INPUT_STREAMS'):
            for stream_class in self.config.INPUT_STREAMS:
                stream = kls_import(stream_class)
                self.input_streams[stream.job_type] = stream()

    def load_reducers(self):
        self.reducers = {}

        if hasattr(self.config, 'REDUCERS'):
            for reducer_class in self.config.REDUCERS:
                reducer = kls_import(reducer_class)
                self.reducers[reducer.job_type] = reducer()


