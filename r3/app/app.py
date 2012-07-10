#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop

from r3.app.handlers.healthcheck import HealthcheckHandler

class R3ServiceApp(tornado.web.Application):

    def __init__(self, context):
        self.context = context

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
        ]

        super(R3ServiceApp, self).__init__(handlers)
