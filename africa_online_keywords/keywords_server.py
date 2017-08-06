# -*- coding:utf-8 -*-
"""
统一后的关键词服务
"""
from core.candidates_word import CandidateKeyword
from core.preconditioning.pre_process import PreProcess
from core.crops_idf import EnIDF
import spacy
import en_core_web_sm
import pickle

#[title_feature, ner_feature, tf, double_tf ,tf_idf, first, last, un_bi]
#[1,             2,           3,  4,         5,      6,     7,    8]

class Keywords(CandidateKeyword):

    def __init__(self,PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE,lan):
        """
        """
        ##配置基本属性
        self.nlp = en_core_web_sm.load()#spacy.load('en_core_web_sm')
        self.language_stem = PreProcess(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE)
        self.idf = EnIDF()
        self.textrank = None
        self.language = lan

        CandidateKeyword.__init__(self,self.nlp, self.language_stem,
                                  self.idf, self.textrank,self.language)

    def __to_unicode(self,input_str):
        """
        编码形式改变
        :param input_str:
        :return:
        """
        if isinstance(input_str, str):
            return unicode(input_str, encoding="utf-8", errors='ignore')
        else:
            return input_str

    def __feature_weight(self, doc_leng):
        """
        调整模型权重系数
        :param candidate:
        :param doc_leng:
        :return:
        """
        for doc in self.__candidate:
            word_feature = self.__candidate[doc]['feature']
            tf_idf = word_feature[4]
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
            self.__candidate[doc]['weight'] = word_weight

    def __filter_result(self, topK):
        """
        过滤结果
        :return:
        """
        token = [(w[0],w[1]['origin_word'],w[1]['weight']) for w in self.__candidate.items()]
        result = sorted(token, key=lambda x:x[2], reverse=True)
        if len(result) == 0:
            self.__result = []
        else:
            token_result = [result[0]]
            for w in result:
                judge = False
                for token_w in token_result:
                    if len(w[0].split()) + len(token_w[0].split()) > len(set(w[0].split() + token_w[0].split())):
                        judge = True
                        break
                if judge is False:
                    token_result.append(w)
                if len(token_result) == topK:
                    break
            self.__result = token_result


    def top_keywords_news(self,title, content, topK):
        """

        :param title:
        :param content:
        :param topK:
        :return:
        """
        title = self.__to_unicode(title)
        content = self.__to_unicode(content)
        self.__candidate,doc_leng = CandidateKeyword.get_candidate_words(self,title,content)
        self.__feature_weight(doc_leng)
        self.__filter_result(topK)
        return {w[0]:w[2] for w in self.__result}

if __name__ == '__main__':
    STOP_FILE = './data/en/stopwords_en.txt'
    PUN_FILE = './data/en/punctuation.txt'
    COMMON_WORDS_FILE = './data/en/common_words_en.txt'
    SPECIAL_FILE = './data/en/special_words_en.txt'

    key = PreProcess(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE)
    key.phrase_process('v4.1.2')
    key_tool = Keywords(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE,'en')

    data = pickle.load(open('./data/in_240_evaluation_0730.pkl', 'r'))
    for doc in data:
        title = data[doc]['title']
        content = data[doc]['content']
        print doc
        print [w[0] for w in data[doc]['new_model_stem']]
        print key_tool.top_keywords_news(title, content, 5).keys()

