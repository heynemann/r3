#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join

class CountWordsStream:
    def process(self, arguments):
        with open(abspath(join(dirname(__file__), 'chekhov.txt'))) as f:
            contents = f.readlines()

        items = []
        current_item = []
        items.append(current_item)
        for line in contents:
            if len(current_item) == 1000:
                current_item = []
                items.append(current_item)
            current_item.append(line.lower())
        return items


