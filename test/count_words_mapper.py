#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time

from r3.worker.mapper import Mapper

class CountWordsMapper(Mapper):
    def map(self, lines):
        #time.sleep(0.5)
        return list(self.split_words(lines))

    def split_words(self, lines):
        for line in lines:
            for word in line.split():
                yield word.strip().strip('.').strip(','), 1

if __name__ == '__main__':
    mapper = CountWordsMapper("count-words", sys.argv[3], redis_host=sys.argv[1], redis_port=int(sys.argv[2]), redis_db=0, redis_pass='r3')
    mapper.run_block()
