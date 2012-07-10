#!/usr/bin/python
# -*- coding: utf-8 -*-

from r3.app.handlers import BaseHandler

class HealthcheckHandler(BaseHandler):
    def get(self):
        self.write('WORKING')

