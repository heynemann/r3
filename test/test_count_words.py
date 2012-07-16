#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from count_words_stream import CountWordsStream
from count_words_reducer import CountWordsReducer

class CountWordsMapper:
    def map(self, lines):
        #time.sleep(0.5)
        return list(self.split_words(lines))

    def split_words(self, lines):
        for line in lines:
            for word in line.split():
                yield word.strip().strip('.').strip(','), 1


def main():
    start = time.time()
    items = CountWordsStream().process(None)
    print "input stream took %.2f" % (time.time() - start)

    start = time.time()
    mapper = CountWordsMapper()
    results = []
    for item in items:
        results.append(mapper.map(item))
    print "mapping took %.2f" % (time.time() - start)

    start = time.time()
    CountWordsReducer().reduce(results)
    print "reducing took %.2f" % (time.time() - start)

if __name__ == '__main__':
    main()
