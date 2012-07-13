#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis

from flask import _app_ctx_stack as stack

class RedisDB(object):

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.config.setdefault('REDIS_HOST', '0.0.0.0')
        app.config.setdefault('REDIS_PORT', 6379)
        app.config.setdefault('REDIS_DB', 0)
        app.config.setdefault('REDIS_PASS', None)

        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def connect(self):
        options = {
            'host': self.app.config['REDIS_HOST'],
            'port': self.app.config['REDIS_PORT'],
            'db': self.app.config['REDIS_DB']
        }

        if self.app.config['REDIS_PASS']:
            options['password'] = self.app.config['REDIS_PASS']

        conn = redis.StrictRedis(**options)
        return conn

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'redis_db'):
            del ctx.redis_db

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'redis_db'):
                ctx.redis_db = self.connect()
            return ctx.redis_db
