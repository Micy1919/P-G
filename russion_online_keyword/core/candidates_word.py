# -*- coding:utf-8 -*-
"""
得到关键词的候选集合
#[title_feature, ner_feature, tf, double_tf ,tf_idf, first, last, un_bi, city, celebrite, text_rank]
#[1,             2,           3,  4,         5,      6,     7,    8,     9,     10,        11]
"""
import string
import dawg
import math

class CandidateKeyword(object):

    def __init__(self, spacy_nlp, stem, IDF, txt_rank, language):
        self.analyzer = stem
        self.nlp = spacy_nlp#nltk_nlp
        self.no_ner_list = [u'CARDINAL', u'ORDINAL', u'DATE', u'LANGUAGE', u'MONEY', u'PERCENT', u'QUANTITY', u'TIME']
        self.city_dawg =None #dawg.DAWG().load('./data/ru/city.dawg')
        self.cele_dawg =None #dawg.DAWG().load('./data/ru/cele.dawg')
        self.idf = IDF
        self.terank = None
        self.__candidate = {}


    def __remove_punctuation(self, text):
        """
        删除最基本的标点符号，人名和地名识别用
        :param text:
        :return:
        """
        exclude = set(string.punctuation)
        for c in exclude:
            text = text.replace(c, ' ')
        return text

    def __get_content_length(self, text):
        """
        得到文章长度
        :param text:
        :return:
        """
        return len(self.analyzer.text_process(text))

    def __get_title_candidate(self, title, deep=True):
        """
        提取标题中的候选关键词
        :param title:
        :return:
        """
        doc = self.nlp(title)
        for w in doc.noun_chunks:
            token = ' '.join(self.analyzer.phrase_process(w.text.encode('utf-8')))
            if not token :continue
            if len(token.split()) > 3 :
                if deep:
                    self.__get_title_candidate(w.text, False)
                continue
            if token not in self.__candidate:
                self.__candidate[token] = {'origin_word': w.text, 'feature': [1, 0, 0, [], 0, 0, 0, 0, 0, 0]}

        for w in doc.ents:
            if w.label_ in self.no_ner_list:
                token = ' '.join(self.analyzer.phrase_process(w.text.encode('utf-8')))
                if token in self.__candidate:
                    del self.__candidate[token]
                continue

            token = ' '.join(self.analyzer.phrase_process(w.text.encode('utf-8')))
            if not token :continue
            if len(token.split()) > 3 :
                if deep:
                    self.__get_title_candidate(w.text, False)
                continue
            if token in self.__candidate:
                self.__candidate[token]['feature'][1] = 1
            else:
                self.__candidate[token] = {'origin_word': w.text, 'feature':[1, 1, 0, [], 0, 0, 0, 0, 0, 0]}

    def __get_content_candidate(self, content, deep=True, pos = 0):
        """
        从正文中提取关键词候选集
        :param content:
        :return:
        """
        doc = self.nlp(content)
        for w in doc.noun_chunks:
            token = ' '.join(self.analyzer.phrase_process(w.text.encode('utf-8')))
            if not token:continue
            if len(token.split()) > 3 :
                if deep:
                    self.__get_content_candidate(w.text,False, 0)
                continue
            if token not in self.__candidate:
                self.__candidate[token] = {'origin_word': w.text, 'feature':[0, 0, 0, [], 0, w.end,
                                                                      w.end,0, 0, 0]}
            else:
                if self.__candidate[token]['feature'][5] == 0:
                    self.__candidate[token]['feature'][5] = w.end
                self.__candidate[token]['feature'][6] = max(w.end,self.__candidate[token]['feature'][6])

        position_weight, ent_num = -1, len(list(doc.ents))
        for w in doc.ents:
            position_weight += 1
            if w.label_ in self.no_ner_list:
                token = ' '.join(self.analyzer.phrase_process(w.text.encode('utf-8')))
                if token in self.__candidate:
                    del self.__candidate[token]
                continue

            token = ' '.join(self.analyzer.phrase_process(w.text.encode('utf-8')))
            if not token :continue
            if len(token.split()) > 3 :
                if deep:
                    self.__get_content_candidate(w.text,False, math.cos(3.14/ent_num/2*position_weight))
                continue
            if token in self.__candidate:
                if deep is False:
                    self.__candidate[token]['feature'][1] = max(pos,self.__candidate[token]['feature'][1])
                else:
                    self.__candidate[token]['feature'][1] = max(math.cos(3.14/ent_num/2*position_weight),
                                                                self.__candidate[token]['feature'][1])
                if self.__candidate[token]['feature'][5] == 0:
                    self.__candidate[token]['feature'][5] = w.end
                self.__candidate[token]['feature'][6] = max(w.end,self.__candidate[token]['feature'][6])
            else:
                self.__candidate[token] = {'origin_word': w.text, 'feature': [0, math.cos(3.14/ent_num/2*position_weight),
                                                                              0, [], 0, w.end,w.end, 0, 0, 0]}


    def __get_city_cele_candidate(self, title, content):
        """
        得到城市，人名的候选链表
        :param title:
        :param content:
        :return:
        """
        text_list = [ w for w in self.__remove_punctuation(title + '. ' + content + 'a,a,a').split() if w]
        for i in range(len(text_list) - 3):
            unigram = text_list[i]
            if self.city_dawg.has_key(unigram):
                token = ' '.join(self.analyzer.phrase_process(unigram.encode('utf-8')))
                if token in self.__candidate:
                    self.__candidate[token]['feature'][8] = 1
                else:
                    self.__candidate[token] =  {'origin_word': unigram,'feature':[0, 0, 0, [], 0, 0, 0, 0, 1, 0]}
            elif self.cele_dawg.has_key(unigram):
                token = ' '.join(self.analyzer.phrase_process(unigram.encode('utf-8')))
                if token in self.__candidate:
                    self.__candidate[token]['feature'][9] = 1
                else:
                    self.__candidate[token] =  {'origin_word': unigram,'feature':[0, 0, 0, [], 0, 0, 0, 0, 0, 1]}

            bigram = ' '.join(text_list[i: i+2])
            if self.cele_dawg.has_key(bigram):
                token = ' '.join(self.analyzer.phrase_process(bigram.encode('utf-8')))
                if token in self.__candidate:
                    self.__candidate[token]['feature'][9] = 1
                else:
                    self.__candidate[token] = {'origin_word': bigram, 'feature': [0, 0, 0, [], 0, 0, 0, 0, 0, 1]}

            trigram = ' '.join(text_list[i: i+3])
            if self.cele_dawg.has_key(trigram):
                token = ' '.join(self.analyzer.phrase_process(trigram.encode('utf-8')))
                if token in self.__candidate:
                    self.__candidate[token]['feature'][9] = 1
                else:
                    self.__candidate[token] = {'origin_word': trigram, 'feature': [0, 0, 0, [], 0, 0, 0, 0, 0, 1]}


    def __get_fr_feature(self,content_list, doc_leng):
        """
        加入频率特征
        :param content_list:
        :param doc_leng:
        :return:
        """
        for doc in self.__candidate:
            if ' ' in doc:
                self.__candidate[doc]['feature'][7] = 1
                fr_feature = ' '.join(content_list).count(doc)/float(doc_leng)
                self.__candidate[doc]['feature'][2] = fr_feature
                for token_doc in doc.split():
                    self.__candidate[doc]['feature'][3].append(content_list.count(token_doc)/float(doc_leng))
                self.__candidate[doc]['feature'][4] = self.idf.tfidf_score(doc, fr_feature,
                                                                           self.__candidate[doc]['feature'][3])
            else:
                fr_feature = content_list.count(doc) / float(doc_leng)
                self.__candidate[doc]['feature'][2] = fr_feature
                self.__candidate[doc]['feature'][4] = self.idf.tfidf_score(doc, fr_feature,
                                                                           self.__candidate[doc]['feature'][3])

    def __get_text_rank_feature(self,):
        """
        提取text_rank分数
        :return:
        """
        for doc in self.__candidate:
            score = self.terank.get_word_score(doc)
            self.__candidate[doc]['feature'].append(score)

    def __normalized(self):
        """
        归一化数据
        :return:
        """
        tf_idf_max = 0
        text_rank_max = 0
        for doc in self.__candidate:
            tf_idf_max = max(self.__candidate[doc]['feature'][4], tf_idf_max)
            text_rank_max = max(self.__candidate[doc]['feature'][10], text_rank_max)
        for doc in self.__candidate:
            self.__candidate[doc]['feature'][4] = self.__candidate[doc]['feature'][4]/tf_idf_max
            self.__candidate[doc]['feature'][10] = self.__candidate[doc]['feature'][10]/text_rank_max
    def __pre_content(self, content):
        """
        处理文章内容出现报社的情况
        :param content:
        :return:
        """
        token_content = content.split(':')
        token_content_ = content.split(',')
        if len(token_content[0].split()) < 3:
            return ':'.join(token_content[1:])
        elif len(token_content_[0].split()) < 3:
            return ','.join(token_content_[1:])
        return content

    def get_candidate_words(self, title, content):
        """
        处理新闻返回候选单词以及各个特征值
        :param title:
        :param content:
        :return:
        """
        self.__candidate = {}
        content = content.encode('utf-8').replace("_line_", '. ').decode('utf-8')
        content = self.__pre_content(content)
        ##text_rank feature
        #content_rank = self.analyzer.text_rank_process(content.encode('utf-8')) +self.analyzer.text_rank_process(title.encode('utf-8'))
        #self.terank.get_content(content_rank)

        content_list = self.analyzer.text_process(content.encode('utf-8')) +self.analyzer.text_process(title.encode('utf-8'))
        doc_leng = len(content_list)
        self.__get_title_candidate(title)
        self.__get_content_candidate(content)
        #self.__get_city_cele_candidate(title, content)
        self.__get_fr_feature(content_list, doc_leng)

        ##text_rank feature
        #self.__get_text_rank_feature()
        #self.__normalized()

        return self.__candidate,doc_leng




