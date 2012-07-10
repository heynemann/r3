#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen

from r3.app.handlers import BaseHandler

class StreamHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        yield tornado.gen.Task(self.redis.set, 'foo', 'something')
        something = yield tornado.gen.Task(self.redis.get, 'foo')

        self.set_header('Content-Type', 'text/html')

        self.write(something)
        self.finish()

