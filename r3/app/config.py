#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import isabs, abspath
import imp

class Config:
    def __init__(self, path):
        if not isabs(path):
            self.path = abspath(path)
        else:
            self.path = path

        self.load()

    def load(self):
        with open(self.path) as config_file:
            name = 'configuration'
            code = config_file.read()
            module = imp.new_module(name)
            exec code in module.__dict__

            for name, value in module.__dict__.iteritems():
                setattr(self, name, value)


