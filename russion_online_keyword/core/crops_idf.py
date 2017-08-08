# -*- coding:utf-8 -*-
"""
idf interface
"""
import json

class EnIDF():
    def __init__(self,):
        self.idf_feature = json.load(open('data/ru/idf_slim.json', 'r'))
        self.avgfl = 1018.9

    def __is_number(self, text):
        """
        判断一个unicode是否是数字
        """
        for uchar in text:
            if uchar >= u'\u0030' and uchar <= u'\u0039':
                continue
            else:
                return False
        return True

    def tfidf_score(self, term, tf, tf_list):
        if ' ' not in term:
            return tf*self.idf_feature.get(term, 2.0)
        bigram_score = 0.0
        term_split = term.split(' ')
        for i in range(len(term_split)):
            if self.__is_number(term_split[i]):
                continue
            bigram_score += tf_list[i]*self.idf_feature.get(term_split[i], 2.0)
        return bigram_score

    def __bm25(self, idf, tf, fl, avgfl, B, K1):
        # idf - inverse document frequency
        # tf - term frequency in the current document
        # fl - field length in the current document
        # avgfl - average field length across documents in collection
        # B, K1 - free paramters
        return idf * ((tf * (K1 + 1)) / (tf + K1 * ((1 - B) + B * fl / avgfl)))

    def bm25_score(self, term, tf, new_leng):
        idf = self.idf_feature.get(term, 5.0)
        score = self.__bm25(idf, tf, new_leng, self.avgfl, 0.75, 1.2)
        return score
