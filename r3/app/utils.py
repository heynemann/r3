#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIMEOUT = 15

def real_import(name):
    if '.'  in name:
        return reduce(getattr, name.split('.')[1:], __import__(name))
    return __import__(name)

logger = logging.getLogger('R3ServiceApp')

def flush_dead_mappers(redis, mappers_key, ping_key):
    mappers = redis.smembers(mappers_key)
    for mapper in mappers:
        last_ping = redis.get(ping_key % mapper)
        if last_ping:
            now = datetime.now()
            last_ping = datetime.strptime(last_ping, DATETIME_FORMAT)
            if ((now - last_ping).seconds > TIMEOUT):
                logging.warning('MAPPER %s found to be inactive after %d seconds of not pinging back' % (mapper, TIMEOUT))
                redis.srem(mappers_key, mapper)
                redis.delete(ping_key % mapper)


def kls_import(fullname):
    if not '.' in fullname:
        return __import__(fullname)

    name_parts = fullname.split('.')
    klass_name = name_parts[-1]
    module_parts = name_parts[:-1]
    module = reduce(getattr, module_parts[1:], __import__('.'.join(module_parts)))
    klass = getattr(module, klass_name)
    return klass


