# -*- coding:utf-8 -*-
import sys
from core.crops_preprocess import CropsPre
from core.crops_idf import EnIDF
#from core.k_means_reslut import KMeansResult
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

#KMeans = KMeansResult()
def feature_weigh(candidate, weight):
    #weight = [0, 0, 0, 0, 20, 0, 0, 0,0]
    for doc in candidate:
        word_feature = candidate[doc]['feature']
        word_feature[3] = sum(word_feature[3])
        #word_weight = sum([weight[i]*word_feature[i] for i in range(8)])
        #candidate[doc]['weight'] = word_weight
        word_weight = np.dot(np.array([word_feature]),weight)
        candidate[doc]['weight'] = word_weight.sum()

    return candidate

def feature_weight_p(candidate):
    for doc in candidate:
        word_feature = candidate[doc]['feature']
        word_weight = 0
        tf_idf = word_feature[4]
        if word_feature[0] == 1:
            word_weight += 1.5*tf_idf
        else:
            word_weight += 1*tf_idf

        if word_feature[1] == 1:
            word_weight += 1.1*tf_idf
        else:
            word_weight += 1.0*tf_idf

        if word_feature[8] == 1 or word_feature[9] == 1:
            word_weight += 1.5*tf_idf
        else:
            word_weight += 1.0*tf_idf

        candidate[doc]['weight'] = word_weight
    return candidate


def caluation_feature(FILE_NAME):
    data = pickle.load(open(FILE_NAME, 'r'))
    STOPWORD = './data/en/stopwords_en.txt'
    STOPLIST = [i.strip() for i in open(STOPWORD, 'r').readlines()]
    nlp = spacy.load('en_core_web_sm')
    text = CropsPre(STOPLIST, nlp)
    tf_idf = EnIDF()
    for docs in data:
        title = data[docs]['title'].decode('utf-8', 'igrone')
        content = data[docs]['content'].decode('utf-8', 'igrone')
        candidate = text.get_candidate_words(title, content)
        for doc in candidate:
            doc_tf = candidate[doc]['feature'][2]
            candidate[doc]['feature'][4] = tf_idf.tfidf_score(doc, doc_tf)
        data[docs]['words'] = candidate
    return data


def get_one_new_keywords(title, content, weight):
    """
    得到一篇文章的关键词
    :param title:
    :param comtemt:
    :param weight:
    :return:
    """
    STOPWORD = './data/en/stopwords_en.txt'
    STOPLIST = [i.strip() for i in open(STOPWORD, 'r').readlines()]
    nlp = spacy.load('en_core_web_sm')
    text = CropsPre(STOPLIST, nlp)
    tf_idf = EnIDF()
    candidate = text.get_candidate_words(title, content)
    for doc in candidate:
        doc_tf = candidate[doc]['feature'][2]
        candidate[doc]['feature'][4] = tf_idf.tfidf_score(doc, doc_tf)
    result = feature_weight_p(candidate, weight)
    result_o = [(result.items()[i][1]['origin_word'], result.items()[i][1]['weight']) for i in xrange(len(result))]
    result_o = sorted(result_o, key=lambda x: x[1], reverse=True)
    result_o = [w[0] for w in result_o[:10]]
    return result_o


if __name__ == '__main__':
    FILE_NAME = './data/in/in_74_new_guideline.pkl'
    num_list = []
    weight = pickle.load(open('./data/in/weight_0716.pkl', 'r'))
    title = u"Now, China moves tonnes of military equipment to Tibet. Should India be scared?"
    content = u"""
    The massive deployment of military might is in northern Tibet, but it will take only six to seven hours for the troops to move to China's side of Nathu La in the Sikkim section.
    People's Liberation Army Navy soldiers take part in an anti-terrorist drill at a naval base. Photo: Reuters
China has moved "tens of thousands of tonnes" of military vehicles and equipment to Tibet, likely under the garb of two defence exercises held on the plateau in recent weeks but perhaps aimed at muscle-flexing amid the Doklam stand-off, said reports today.

The massive beefing up of logistics was not near the Sikkim border but in northern Tibet, near Xinjiang in the west. Beijing can, however, rapidly deploy its logistics to the border through its vast road and rail network in Tibet, with the expressway now extending from Lhasa all the way to Yadong, on China's side of Nathu La in the Sikkim section. The 700 km distance can be covered in six to seven hours.

"The vast haul was transported to a region south of the Kunlun Mountains in northern Tibet by the Western Theatre Command - which oversees the restive regions of Xinjiang and Tibet, and handles border issues with India," the PLA Daily, official newspaper of the military, was quoted as saying by the South China Morning Post.

The report said the project "took place late last month" and "involved hardware being moved simultaneously by road and rail from across the entire region".

WHAT IS THE PLA UP TO?

The PLA Daily did not say if the logistics movement was for the two exercises. On July 3, State media reported on drills involving a new battle tank, while this past weekend, a live-fire drill and testing of anti-aircraft guns was held on the plateau by a mountain brigade responsible for frontier combat operations.

Ni Lexiong, a Shanghai-based military commentator, told the South China Morning Post the movement was "likely related to the stand-off and could have been designed to bring India to the negotiating table."

"Diplomatic talks must be backed by military preparation," he was quoted as saying.

"The PLA wanted to demonstrate it could easily overpower its Indian counterparts," added military commentator Zhou Chenming to the paper.

Wang Dehua, a South Asia strategic expert, told the paper that "military operations are all about logistics" and at present "there is much better logistics support to the Tibet region."

"China is also different from [how it was in] 1962", Wang was quoted as saying, noting that in 1962, "logistics difficulties contributed to [China] pulling back and declaring a unilateral ceasefire."

Now, he added, the PLA can "easily transport troops and supplies to the frontline, thanks to the much improved infrastructure including the Qinghai-Tibet railway and other new roads connecting the plateau to the rest part of China."
    """
    print get_one_new_keywords(title,content,weight)
    """
    data = caluation_feature(FILE_NAME)
    num = 0
    for doc in data:
        candidate = copy.deepcopy(data[doc]['words'])
        candidate = feature_weigh(candidate, weight)
        #result = KMeans.k_means_result(candidate)
        result = candidate
        result_o = [(result.items()[i][0], result.items()[i][1]['weight']) for i in xrange(len(result))]
        result_o = sorted(result_o, key=lambda x: x[1], reverse=True)
        result_o = [w[0] for w in result_o[:5]]

        result_k = []
        for label in range(5):
            token_result = [(result.items()[i][0], result.items()[i][1]['weight']) for i in xrange(len(result))
                            if result.items()[i][1]['k_means'] == label]
            token_result = sorted(token_result, key=lambda x: x[1], reverse=True)
            if len(token_result) > 0:
                result_k.append(token_result[0][0])
        num += len([w for w in result_k if w in data[doc]['guideline']])
        print 'title :',data[doc]['title']
        print 'content :',data[doc]['content']
        print '**********************************'
        #print 'guide line :',data[doc]['guideline']
        print 'keywords :',data[doc]['keywords']
        print 'supervised_keywords :',data[doc]['supervised_keywords']
        print 'new_model :',result_o
        print 'new_model_k_means: ',result_k
        print num
    """


