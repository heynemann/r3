#!/usr/bin/python
# -*- coding: utf-8 -*-

from r3.worker.mapper import Mapper

class CountWordsMapper(Mapper):
    job_type = 'count-words'

    def map(self, lines):
        #time.sleep(0.5)
        return list(self.split_words(lines))

    def split_words(self, lines):
        for line in lines:
            for word in line.split():
                yield word.strip().strip('.').strip(','), 1
