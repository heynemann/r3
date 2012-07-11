#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join

class CountWordsStream:
    def process(self, arguments):
        with open(abspath(join(dirname(__file__), 'small-chekhov.txt'))) as f:
            contents = f.readlines()

        return [line.lower() for line in contents]


