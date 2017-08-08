# -*- coding:utf-8 -*-
"""
统一后的关键词服务
"""
from core.candidates_word import CandidateKeyword
from core.preconditioning.pre_process import PreProcess
from core.crops_idf import EnIDF
import spacy

import pickle
import numpy as np
import os
import random
import copy
import math
import json
#[title_feature, ner_feature, tf, double_tf ,tf_idf, first, last, un_bi]
#[1,             2,           3,  4,         5,      6,     7,    8]

class keywords_tool(object):
    def __init__(self,STOP_FILE = 'in_keywords/data/en/stopwords_en.txt',PUN_FILE = 'in_keywords/data/en/punctuation.txt',
                 SPECIAL_FILE='in_keywords/data/en/special_words_en.txt', COMMON_WORDS_FILE = 'in_keywords/data/en/common_words_en.txt'):
        print 'keywords_tool start'
        print '加载模型'
        self.nlp = spacy.load('en_core_web_sm')
        self.en_stem = PreProcess(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE)
        self.idf = EnIDF()
        self.candidate_tool = CandidateKeyword(self.nlp, self.en_stem, self.idf, 'in')
        print '加载成功'

    def get_one_new_keywords(self,title, content):
        """
        得到一篇文章的关键词
        :param title:
        :param comtemt:
        :param weight:
        :return:
        """

        candidate, doc_leng = self.candidate_tool.get_candidate_words(title, content)
        result = self.feature_weight_p(candidate, doc_leng)
        result = [(result.items()[i][0], result.items()[i][1]['weight']) for i in xrange(len(result))]
        result = sorted(result, key=lambda x: x[1], reverse=True)
        result = self.filter_result_(result)
        result = [w[0].decode('utf-8') for w in result[:5]]
        return result




    def filter_result_(self, result):
        """

        :param result:
        :return:
        """
        mid_result = [result[0]]
        for w in result:
            judge = False
            for token_w in mid_result:
                if len(w[0].split()) + len(token_w[0].split()) > len(set(w[0].split() + token_w[0].split())):
                    judge = True
                    break
            if judge is False:
                mid_result.append(w)
        return mid_result



    def feature_weight_p(self, candidate, doc_leng):
        """
        权重系数的调整
        :param candidate:
        :param doc_leng:
        :return:
        """

        for doc in candidate:
            word_feature = candidate[doc]['feature']
            word_weight = 0
            tf_idf = word_feature[4]
            if word_feature[0] == 1:
                if word_feature[1] == 1:
                    word_weight = 9 * tf_idf
                else:
                    word_weight = 6 * tf_idf
            else:
                if word_feature[1] == 1:
                    if word_feature[5] < doc_leng/10:
                        if word_feature[8] == 1 or word_feature[9] == 1:
                            word_weight = 3 * tf_idf
                        else:
                            word_weight = 1.5 * tf_idf
                    else:
                        if word_feature[8] == 1 or word_feature[9] == 1:
                            word_weight = 2 * tf_idf
                        else:
                            word_weight = 1.5 * tf_idf
                else:
                    if word_feature[5] < doc_leng/10:
                        if word_feature[8] == 1 or word_feature[9] == 1:
                            word_weight = 2*tf_idf
                        else:
                            word_weight = 1.8 * tf_idf
                    else:
                        if word_feature[8] == 1 or word_feature[9] == 1:
                            word_weight = 2 * tf_idf
                        else:
                            word_weight = 1.8 * tf_idf
            candidate[doc]['weight'] = word_weight
        return candidate


if __name__ == '__main__':
    FILE_NAME = './data/in/in_235_evaluation_0720.pkl'


