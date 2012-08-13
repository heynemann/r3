#!/usr/bin/python
# -*- coding: utf-8 -*-

from r3.app.handlers import BaseHandler
from r3.app.keys import MAPPERS_KEY
from r3.version import __version__

class IndexHandler(BaseHandler):
    def get(self):
        has_reducers = len(self.application.reducers.keys()) > 0

        self.render(
            "../templates/index.html", 
            title="",
            r3_version=__version__,
            input_streams=self.application.input_streams.keys(),
            has_reducers=has_reducers,
            mappers=self.get_mappers()
        )

    def get_mappers(self):
        return self.redis.smembers(MAPPERS_KEY)


