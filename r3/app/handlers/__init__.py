#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.web

from r3.app.utils import logger

class BaseHandler(tornado.web.RequestHandler):
    def _error(self, status, msg=None):
        self.set_status(status)
        if msg is not None:
            logger.error(msg)
        self.finish()

    @property
    def redis(self):
        return self.application.redis


