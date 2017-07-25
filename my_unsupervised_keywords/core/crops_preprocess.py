# -*- coding:utf-8
"""
自己的无监督关键词提取模型
"""
import string
import re
import copy
import pickle
from whoosh.analysis import StemmingAnalyzer
#[title_feature, ner_feature, tf, double_tf ,tf_idf, first, last, un_bi, city_or_cele]
#[1,             2,           3,  4,         5,      6,     7,    8, 9]

class CropsPre(object):

    def __init__(self, STOPLIST, spacy_nlp):
        self.analyzer = StemmingAnalyzer(stoplist=STOPLIST)
        self.nlp = spacy_nlp
        self.no_ner_list = [u'CARDINAL', u'ORDINAL', u'DATE', u'LANGUAGE', u'MONEY', u'PERCENT', u'QUANTITY', u'TIME']
        self.city_cele_dic = pickle.load(open('./data/in/city_and_cele_dic.pkl', 'r'))

    def stem_text(self, text):
        ret = []
        for token in text:
            stem_k = [i.text for i in self.analyzer(token)]
            if stem_k:
                ret.append(' '.join(stem_k))
            else:
                continue
        return ret

    def remove_punctuation(self, text):
        remove_list = [u'\u2018s', u'\u2018']
        remove_list_1 = ['_line_']
        for w in remove_list:
            text = text.replace(w, '')
        for w in remove_list_1:
            text = text.replace(w, ' ')
        """
        exclude = set(string.punctuation+''.join([i for i in text if ord(i) >= 128]))
        for c in exclude:
            text = text.replace(c, ' ')
        """
        return text

    def get_content_length(self, text):
        return len(self.stem_text(text.split()))


    def get_title_candidate(self, title):
        candidate = {}
        doc = self.nlp(title)
        for w in doc.noun_chunks:
            token = ' '.join(self.stem_text(w.text.split()))
            if not token: continue
            if len(token.split()) > 3:continue
            if token not in candidate:
                candidate[token] = {'origin_word': w.text, 'feature': [1,0,0,[],0,0,0,0,0]}
                if w.text in self.city_cele_dic:
                    candidate[token]['feature'][8] = 1
        for w in doc.ents:
            if w.label_ in self.no_ner_list:
                token = ' '.join(self.stem_text(w.text.split()))
                if token in candidate:
                    del candidate[token]
                continue

            token = ' '.join(self.stem_text(w.text.split()))
            if not token: continue
            if len(token.split()) > 3:continue
            if token in candidate:
                candidate[token]['ner_feature'] = 1
                if w.text in self.city_cele_dic:
                    candidate[token]['feature'][8] = 1
            else:
                candidate[token] = {'origin_word': w.text, 'feature':[1,1,0,[],0,0,0,0,0]}
                if w.text in self.city_cele_dic:
                    candidate[token]['feature'][8] = 1
        return candidate

    def get_content_candidate(self, content):
        candidate = {}
        doc = self.nlp(content)
        doc_leng = self.get_content_length(content)
        for w in doc.noun_chunks:
            token = ' '.join(self.stem_text(w.text.split()))
            if not token: continue
            if len(token.split()) > 3: continue
            if token not in candidate:
                candidate[token] = {'origin_word': w.text, 'feature':[1,0,0,[],0,w.end/float(doc_leng),
                                                                      w.end / float(doc_leng),0,0]}
                if w.text in self.city_cele_dic:
                    candidate[token]['feature'][8] = 1
            else:
                candidate[token]['feature'][6] = w.end/float(doc_leng)

        for w in doc.ents:
            if w.label_ in self.no_ner_list:
                token = ' '.join(self.stem_text(w.text.split()))
                if token in candidate:
                    del candidate[token]
                continue

            token = ' '.join(self.stem_text(w.text.split()))
            if not token: continue
            if len(token.split()) > 3: continue
            if token in candidate:
                candidate[token]['feature'][1] = 1
                candidate[token]['feature'][6] = max(candidate[token]['feature'][6], w.end/float(doc_leng))
            else:
                candidate[token] = {'origin_word': w.text,'feature':[1,1,0,[],0,w.end/float(doc_leng),
                                                                      w.end / float(doc_leng), 0,0]}
                if w.text in self.city_cele_dic:
                    candidate[token]['feature'][8] = 1
        return candidate

    def get_candidate_words(self, title, content):
        title = self.remove_punctuation(title)
        content = self.remove_punctuation(content)
        title_words = self.get_title_candidate(title)
        #print title_words
        candidate_words = self.get_content_candidate(content)
        for doc in title_words:
            if doc in candidate_words:
                candidate_words[doc]['feature'] = \
                    [title_words[doc]['feature'][i] + candidate_words[doc]['feature'][i]
                     for i in range(9)]
            else:
                candidate_words[doc] = title_words[doc]
        text = title + '. ' + content
        doc_leng = self.get_content_length(text)
        text = ' '.join(self.stem_text(text.split()))
        for w in candidate_words:
            if ' ' in w:
                candidate_words[w]['feature'][7] = 1
                candidate_words[w]['feature'][2] = text.count(w)/float(doc_leng)
                candidate_words[w]['feature'][3] = \
                    [text.count(token)/float(doc_leng) for token in w.split()]
            else:
                candidate_words[w]['feature'][2] = text.count(w)/float(doc_leng)
        return candidate_words



