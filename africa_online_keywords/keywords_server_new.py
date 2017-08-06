# -*- coding:utf-8 -*-
"""
统一后的关键词服务
"""
from core.candidates_word import CandidateKeyword
from core.preconditioning.pre_process import PreProcess
from core.crops_idf import EnIDF
from core.text_rank import TextRank
import spacy
import pickle

import os
import random
import copy
import math
import json
#[title_feature, ner_feature, tf, double_tf ,tf_idf, first, last, un_bi]
#[1,             2,           3,  4,         5,      6,     7,    8]
print '加载模型'
STOP_FILE = './data/en/stopwords_en.txt'
PUN_FILE = './data/en/punctuation.txt'
COMMON_WORDS_FILE = './data/en/common_words_en.txt'
SPECIAL_FILE = './data/en/special_words_en.txt'
nlp = spacy.load('en_core_web_sm')
en_stem = PreProcess(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE)
idf = EnIDF()
candidate_tool = CandidateKeyword(nlp, en_stem, idf, TextRank,'in')
print '加载成功'



def caluation_feature(FILE_NAME):
    """
    计算新闻的特征
    :param FILE_NAME:
    :return:
    """
    data = pickle.load(open(FILE_NAME, 'r'))
    for docs in data:
        #if docs != 'c5581482':continue
        title = data[docs]['title'].decode('utf-8', 'igrone')
        content = data[docs]['content'].decode('utf-8', 'igrone')
        candidate, doc_leng = candidate_tool.get_candidate_words(title, content)
        data[docs]['words'] = candidate
        data[docs]['content_leng'] = doc_leng
    return data


def get_one_new_keywords(title, content):
    """
    得到一篇文章的关键词
    :param title:
    :param comtemt:
    :param weight:
    :return:
    """

    candidate, doc_leng = candidate_tool.get_candidate_words(title, content)
    result = feature_weight_p(candidate, doc_leng)
    result = [(result.items()[i][0], result.items()[i][1]['weight']) for i in xrange(len(result))]
    result = sorted(result, key=lambda x: x[1], reverse=True)
    result = [w[0].decode('utf-8') for w in result[:10]]
    return result


def filter_result(result):
    """
    过滤重复的结果
    :param result:
    :return:
    """
    if len(result) == 0:
        return result
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



def feature_weight(candidate, doc_leng):
    """
    权重系数的调整
    :param candidate:
    :param doc_leng:
    :return:
    """
    for doc in candidate:
        word_feature = candidate[doc]['feature']
        tf_idf = word_feature[4]
        if word_feature[0] == 1:
            if word_feature[1] != 0:
                word_weight = (9 + 6*word_feature[1]) * tf_idf
            else:
                word_weight = 7 * tf_idf
        else:
            if word_feature[1] == 100:
                if word_feature[8] == 1 or word_feature[9] == 1:
                    word_weight = (3 + word_feature[1]*2.5/2) * tf_idf
                else:
                    word_weight = (1.5 + word_feature[1]*1.5/2) * tf_idf
            elif word_feature[1] != 0:
                if word_feature[8] == 1 or word_feature[9] == 1:
                    word_weight = (3 + word_feature[1]*2.5) * tf_idf
                else:
                    word_weight = (1.5 + word_feature[1]*1.5) * tf_idf
            else:
                if word_feature[8] == 1 or word_feature[9] == 1:
                    word_weight = 4*tf_idf
                else:
                    if word_feature[5] < float(doc_leng) / 5:
                        word_weight = 2 * tf_idf
                    else:
                        word_weight = 1.5 * tf_idf
        candidate[doc]['weight'] = word_weight
    return candidate

def feature_weight_tf_rank(candidate, doc_leng):
    """
    计算tf_idf权重以及text_rank权重
    :param candidate:
    :param doc_leng:
    :return:
    """
    for doc in candidate:
        word_feature = candidate[doc]['feature']
        tf_idf = word_feature[4] + word_feature[10]
        if word_feature[0] == 1:
            if word_feature[1] != 0:
                word_weight = (9 + 6 * word_feature[1]) * tf_idf
            else:
                word_weight = 7 * tf_idf
        else:
            if word_feature[1] == 100:
                if word_feature[8] == 1 or word_feature[9] == 1:
                    word_weight = (3 + word_feature[1] * 2.5 / 2) * tf_idf
                else:
                    word_weight = (1.5 + word_feature[1] * 1.5 / 2) * tf_idf
            elif word_feature[1] != 0:
                if word_feature[8] == 1 or word_feature[9] == 1:
                    word_weight = (3 + word_feature[1] * 2.5) * tf_idf
                else:
                    word_weight = (1.5 + word_feature[1] * 1.5) * tf_idf
            else:
                if word_feature[8] == 1 or word_feature[9] == 1:
                    word_weight = 4 * tf_idf
                else:
                    if word_feature[5] < float(doc_leng) / 5:
                        word_weight = 2 * tf_idf
                    else:
                        word_weight = 1.5 * tf_idf
        candidate[doc]['weight'] = word_weight
    return candidate

if __name__ == '__main__':
    FILE_NAME = './data/in/in_235_evaluation_0720.pkl'
    weight = pickle.load(open('./data/in/weight_0719.pkl', 'r'))

    data = caluation_feature(FILE_NAME)
    for doc in data:
        print doc
        doc_leng = data[doc]['content_leng']
        candidate = copy.deepcopy(data[doc]['words'])
        candidate = feature_weight(candidate, doc_leng)
        # result = KMeans.k_means_result(candidate)
        result = copy.deepcopy(candidate)
        result = [(result.items()[i][0],result.items()[i][1]['origin_word'], result.items()[i][1]['weight']) for i in xrange(len(result))]
        result = sorted(result, key=lambda x: x[2], reverse=True)
        result = filter_result(result)

        data[doc]['new_model'] = [w[1] for w in result[:5]]
        data[doc]['new_model_stem'] = [w[0] for w in result[:5]]
        print 'tf_model: ',[w[0] for w in result[:5]]
        #ner
        result_ner = copy.deepcopy(candidate)
        result_ner = [(result_ner.items()[i][0], result_ner.items()[i][1]['origin_word'], result_ner.items()[i][1]['weight']) for i in
                  xrange(len(result_ner)) if result_ner.items()[i][1]['feature'][1] == 1]
        result_ner = sorted(result_ner, key=lambda x: x[2], reverse=True)
        result_ner = [w[1] for w in result_ner[:5]]
        data[doc]['new_model_ner'] = result_ner

        candidate = feature_weight_tf_rank(candidate,doc_leng)
        result = copy.deepcopy(candidate)
        result = [(result.items()[i][0], result.items()[i][1]['origin_word'], result.items()[i][1]['weight']) for i in
                  xrange(len(result))]
        result = sorted(result, key=lambda x: x[2], reverse=True)
        result = filter_result(result)
        data[doc]['tf_rank'] = [w[1] for w in result[:5]]
        data[doc]['tf_rank_srem'] = [w[0] for w in result[:5]]
        print 'tf_rank_model: ',[w[0] for w in result[:5]]
        print '---------------------------------------'
        print '\n\n'
        #print data[doc]['keywords']
    #pickle.dump(data, open('in_235_evaluation_0801.pkl', 'w'))

