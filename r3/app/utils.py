#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

def real_import(name):
    if '.'  in name:
        return reduce(getattr, name.split('.')[1:], __import__(name))
    return __import__(name)

logger = logging.getLogger('R3ServiceApp')
