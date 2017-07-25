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
print '加载模型'
STOP_FILE = './data/en/stopwords_en.txt'
PUN_FILE = './data/en/punctuation.txt'
COMMON_WORDS_FILE = './data/en/common_words_en.txt'
SPECIAL_FILE = './data/en/special_words_en.txt'
nlp = spacy.load('en_core_web_sm')
en_stem = PreProcess(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE)
idf = EnIDF()
candidate_tool = CandidateKeyword(nlp,en_stem,idf,'in')
print '加载成功'

#KMeans = KMeansResult()
def feature_weigh(candidate, weight):
    for doc in candidate:
        word_feature = candidate[doc]['feature']
        word_feature[3] = sum(word_feature[3])
        #word_weight = sum([weight[i]*word_feature[i] for i in range(8)])
        #candidate[doc]['weight'] = word_weight
        word_weight = np.dot(np.array([word_feature]),weight)
        candidate[doc]['weight'] = word_weight.sum()

    return candidate


def caluation_feature(FILE_NAME):
    """
    计算新闻的特征
    :param FILE_NAME:
    :return:
    """
    data = pickle.load(open(FILE_NAME, 'r'))
    for docs in data:
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
    过滤最终的排序结果,原始词不是大写且小于2的都过滤掉
    :param result:
    :return:
    """
    result_list = range(5)
    result_i = 5
    while True:
        unigram = [(result[i][0].encode('utf-8'),i) for i in result_list if ' ' not in result[i][0]]
        no_unigram = []
        for w in unigram:
            token = [result[i][0].encode('utf-8') for i in result_list if ' ' in result[i][0]]
            for token_w in token:
                if w[0] in token_w:
                    no_unigram.append(w[1])
                    break
        trgram = [(result[i][0].encode('utf-8'),i) for i in result_list if len(result[i][0].split()) == 2]
        no_trgram = []
        for w in trgram:
            token = [result[i][0].encode('utf-8') for i in result_list if len(result[i][0].split()) == 3]
            for token_w in token:
                if w[0] in token_w:
                    no_trgram.append(w[1])
                    break
        all_repeat_word = no_unigram[:] + no_trgram[:]
        if len(all_repeat_word) == 0 or result_i > len(result):
            break
        else:
            result_list = result_list[:] + range(result_i, result_i + len(all_repeat_word))
            result_list = [i for i in result_list if i not in all_repeat_word]
            result_i += len(all_repeat_word)

    return [result[i] for i in result_list]

def filter_result_(result):
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



def feature_weight_p(candidate, doc_leng):
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

def get_news_keywords(title, content):
    """
    得到一篇文章的关键词
    :param title:
    :param content:
    :return:
    """

if __name__ == '__main__':
    FILE_NAME = './data/in/in_235_evaluation_0720.pkl'
    num_list = []
    weight = pickle.load(open('./data/in/weight_0719.pkl', 'r'))
    #row = np.array([0,0,0,0,0,0,0,0,0])
    #column = np.array([0,0,0,0,0,0,0,0,0,0])
    #weight = np.row_stack((weight, row))
    #weight = np.column_stack((weight, column))

    data = caluation_feature(FILE_NAME)
    for doc in data:
        if doc == '6f9c11b6':
            print 'start'
        doc_leng = data[doc]['content_leng']
        candidate = copy.deepcopy(data[doc]['words'])
        candidate = feature_weight_p(candidate, doc_leng)
        # result = KMeans.k_means_result(candidate)
        result = copy.deepcopy(candidate)
        result = [(result.items()[i][0],result.items()[i][1]['origin_word'], result.items()[i][1]['weight']) for i in xrange(len(result))]
        result = sorted(result, key=lambda x: x[2], reverse=True)
        result = filter_result_(result)
        #result = [w[1] for w in result[:5]]
        data[doc]['new_model'] = [w[1] for w in result[:5]]
        data[doc]['new_model_stem'] = [w[0] for w in result[:5]]
        #ner
        result_ner = copy.deepcopy(candidate)
        result_ner = [(result_ner.items()[i][0], result_ner.items()[i][1]['origin_word'], result_ner.items()[i][1]['weight']) for i in
                  xrange(len(result_ner)) if result_ner.items()[i][1]['feature'][1] == 1]
        result_ner = sorted(result_ner, key=lambda x: x[2], reverse=True)
        result_ner = [w[1] for w in result_ner[:5]]
        data[doc]['new_model_ner'] = result_ner
        #print doc
        print [w[1] for w in result[:]]
        #print candidate
        print '---------------------------------------'
        #print data[doc]['keywords']
    pickle.dump(data, open('./in_235_evaluation_0725.pkl', 'w'))
    best_result = 0
    while False:
        num = 0
        weight_new = copy.deepcopy(weight)
        for _ in range(random.sample(xrange(10), 1)[0]):
            weight_i, weight_j = random.sample(xrange(10), 1)[0], random.sample(xrange(10),1)[0]
            weight_new[weight_i][weight_j] = np.random.random_sample()*50 - 25
        for doc in data:
            candidate = copy.deepcopy(data[doc]['words'])
            candidate = feature_weigh(candidate, weight_new)
            #result = KMeans.k_means_result(candidate)
            result = candidate
            result = [(result.items()[i][0], result.items()[i][1]['weight']) for i in xrange(len(result))]
            result = sorted(result, key=lambda x: x[1], reverse=True)
            result = [w[0] for w in result[:5]]
            num += len([w for w in result if w in data[doc]['guideline']])
        if num > best_result:
            best_result = num
            weight = copy.deepcopy(weight_new)
            pickle.dump(weight_new, open('./data/in/weight_0719.pkl','w'))
            print 'best_result',num

