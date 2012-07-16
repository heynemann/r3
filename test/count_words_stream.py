#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join

class CountWordsStream:
    group_size = 1000

    def process(self, arguments):
        with open(abspath(join(dirname(__file__), 'chekhov.txt'))) as f:
            contents = f.readlines()

        return [line.lower() for line in contents]


