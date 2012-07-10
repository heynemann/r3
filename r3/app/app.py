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
            (r'/stream', StreamHandler),
        ]

        super(R3ServiceApp, self).__init__(handlers)
