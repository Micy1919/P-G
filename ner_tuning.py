# -*- coding:utf-8 -*-
"""
完成ner的抽取测试，以美国的为例子，找到一个最好的抽取标准
"""
import re
import pickle
import copy
import spacy
import string
from whoosh.analysis import StemmingAnalyzer
STOPLIST = [i.strip() for i in open('model_data/en/stoplist_us.txt', 'r').readlines()]
ana = StemmingAnalyzer(stoplist=STOPLIST)


class EnglishStemmer(object):

    def __init__(self):
        self.analyzer = ana

    def stem_text(self, text):
        ret = []
        for token in text:
            stem_k = [i.text for i in ana(token.decode('utf-8'))]
            if stem_k:
                ret.append(' '.join(stem_k))
            else:
                ret.append('')
        return ret


def remove_punctuation(text):
    exclude = set(string.punctuation+''.join([i for i in text if ord(i) >= 128]))
    for c in exclude:
        text = text.replace(c, ' ')
    return text


stem = EnglishStemmer()
nlp = spacy.load('en_core_web_md')
CROPS_FILE = './data/en/train_data_0207.pkl'


def get_content_length(content):
    return len(re.split(' |\n', remove_punctuation(content)))


def content_entity(data = None, weight = 0):
    if data == None:
        data = pickle.load(open(CROPS_FILE, 'r'))
    title_num_ner = 0
    content_num_ner = 0
    for doc in data:
        title = data[doc]['title']
        content = data[doc]['content']
        content_lengt = get_content_length(content)/10
        docs = nlp(title)
        ent1_list = [(ent.text, ent.label_) for ent in docs.ents]
        docs = nlp(content)
        ent2_list = [(ent.text, ent.label_) for ent in docs.ents if content.count(ent.text)/float(content_lengt) > weight]
        title_num_ner += len(ent1_list)
        content_num_ner += len(ent2_list)
        data[doc]['all_entity'] = list(set(ent1_list + ent2_list))
    #
    no_ner_list = [u'CARDINAL', u'ORDINAL', u'DATE', u'LANGUAGE', u'MONEY', u'PERCENT', u'QUANTITY', u'TIME']
    for doc in data:
        enr_token = data[doc]['all_entity']
        data[doc]['all_entity'] = [w for w in enr_token if w[1] not in no_ner_list]
    ner_list = {}
    for doc in data:
        enr_token = data[doc]['all_entity']
        for w in enr_token:
            if w[1] not in ner_list:
                ner_list[w[1]] = w[0]
    #
    num_g = 0
    num_n = 0
    for doc in data:
        ner_list = data[doc]['all_entity']
        num_n += len(data[doc]['all_entity'])
        ner_list = [' '.join(stem.stem_text(remove_punctuation(ent[0]).split())) for ent in ner_list]
        ner_token = []
        for w in ner_list:
            if ' ' in w:
                for w1 in w.split():
                    ner_token.append(w1)
            else:
                ner_token.append(w)
        golden_set_keywords = data[doc]['golden_set_keywords']
        # print ner_token
        golden = []
        for w in golden_set_keywords:
            bp = 1
            for w1 in w.split():
                if w1 in ner_token:
                    golden.append(w)
                    break
        # print golden,ner_list,data[doc]['title']
        data[doc]['golden_set_keywords'] = [w for w in golden_set_keywords if w not in golden]
        num_g += len(golden)
    print 'num_golden have ner:', num_g
    print 'num_news have ner:', num_n
    return num_g, num_n

if __name__ == '__main__':
    weight_list = [i/float(100) for i in range(100)]
    weitht_dic = {}
    for wei in weight_list:
        token_g, token_n = content_entity(None, wei)
        weitht_dic[wei] = {'num_goledn_ner': token_g, 'num_news_ner':token_n}
        print '----------------',wei,'------------------'
    pickle.dump(weitht_dic, open('./ner_tuning.pkl', 'w'))


