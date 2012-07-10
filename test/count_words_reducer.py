#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict

class CountWordsReducer:
    def reduce(self, items):
        word_freq = defaultdict(int)
        for line in items:
            for word, frequency in line:
                word_freq[word] += frequency

        return word_freq
