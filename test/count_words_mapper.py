#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from r3.worker.mapper import FastMapper, ForkMapper, SafeMapper

class CountWordsMapper(SafeMapper):
    def map(self, line):
        return list(self.split_words(line))

    def split_words(self, line):
        for word in line.split():
            yield word.strip().strip('.').strip(','), 1

if __name__ == '__main__':
    mapper = CountWordsMapper("count-words", sys.argv[3], redis_host=sys.argv[1], redis_port=int(sys.argv[2]), redis_db=0, redis_pass='r3')
    mapper.run_block()
