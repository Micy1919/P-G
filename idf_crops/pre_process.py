# -*- coding:utf-8 -*-
__author__ = 'chenjun'

import nltk
from nltk.stem.porter import PorterStemmer
import re
import string


class pre_process(object):
    def __init__(self, punctuation_file, stopwords_file, special_terms=["_line_"]):
        self.punctuation = set([line.strip() for line in open(punctuation_file, "r")])
        self.stopwords = set([line.strip() for line in open(stopwords_file, "r")])
        self.special_terms = special_terms

    def __del_special_terms(self, text):
        """
        删除指定特殊字符。
        :param text: 文本
        :return:
        """
        for s_term in self.special_terms:
            text = text.replace(s_term, " ")
        return text


    def __del_punctution(self, text):
        """
        删除标点符号。
        :param text: 文本
        :return:
        """
        text = text.replace("'s", " is")
        text = text.replace("'m", " am")
        text = text.replace("'re", " are")
        text = text.replace("'ve", " have")
        for punct in self.punctuation:
            text = text.replace(punct, "")
        return text

    def __tokenize(self, text):
        """
        按空格分词。
        :param text: 文本
        :return:
        """
        terms = [term for term in text.split(" ") if term != '']
        return terms

    def __del_stopwords(self, terms):
        """
        去除停用词。
        :param terms: 单词列表
        :return:
        """
        terms = [term for term in terms if term not in self.stopwords]
        return terms

    def __stem(self, terms):
        """
        词干化。
        :param terms: 单词列表
        :return:
        """
        terms = [PorterStemmer().stem(term.lower()) for term in terms]
        return terms

    def __is_number(self, uchar):
        """
        判断一个unicode是否是数字
        """
        if uchar >= u'\u0030' and uchar <= u'\u0039':
            return True
        else:
            return False

    def __is_alphabet(self, uchar):
        """
        判断一个unicode是否是英文字母
        """
        if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
            return True
        else:
            return False

    def __is_local_for_text(self, terms):
        """
        判断文本单词中是否是存在非local字符，如存在去除单词。
        :param terms:
        :return:
        """
        words = []
        for term in terms:
            flag = True
            term = term.decode("utf8")
            for w in term:
                if not (self.__is_alphabet(w) or self.__is_number(w)):
                    flag = False
            if flag:
                words.append(term)
        return words

    def __is_local_for_phrase(self, terms):
        """
        判断候选短语单词中是否存在非local字符， 如存在，则舍弃短语。
        :param terms: 候选短语单词
        :return:
        """
        flag = True
        for term in terms:
            term = term.decode("utf8")
            for w in term:
                if not (self.__is_alphabet(w) or self.__is_number(w)):
                    flag = False
        if flag:
            return terms
        else:
            return []

    def phrase_process(self, phrase):
        """
        短语或单词预处理。
        :param phrase: 短语，string
        :return:
        """
        phrase = self.__del_punctution(self.__del_special_terms(phrase.lower()))
        terms = self.__del_stopwords(self.__tokenize(phrase))
        terms = self.__stem(self.__is_local_for_phrase(terms))
        return terms

    def text_process(self, text):
        """
        文本预处理。
        :param text: 文本, string
        :return:
        """
        text = self.__del_punctution(self.__del_special_terms(text.lower()))
        terms = self.__del_stopwords(self.__tokenize(text))
        terms = self.__stem(self.__is_local_for_text(terms))
        return terms


if __name__ == "__main__":
    text = "Bell Bay Alumini我um says the energy crisis has sent shockwaves through its customer base. Bell Bay Aluminium says the energy crisis has sent shockwaves through its customer base, and for the first time in\\u00a025 years it\\u2019s had to inform some international\\u00a0buyers\\u00a0it can\\u2019t supply them. The Northern company, which is Tasmania\\u2019s largest power user, has\\u00a0reduced its aluminium production by 10,000 tonnes in an effort to save energy. General manager Ray Mostogl told a Senate inquiry in Hobart on Thursday that it will cost the company $22 million in lost revenue. \\u201cWe\\u2019ve been very reliant suppliers in the market, this is a unique situation,\\u201d Mr Mostogl said. \\u201cWe\\u2019ve had to notify Asian-based customers that we can\\u2019t supply them. \\u201cIt\\u2019s not a great thing when commodity prices are as low as they are.\\u201d Mr Mostogl said the company would have to work hard to build its reputation back up. \\u201cThere\\u2019s plenty of other smelters chasing those markets,\\u201d he said. The company voluntarily negotiated a load reduction with Hydro Tasmania, and Mr Mostogl said it was also a moral obligation. \\u201cWe are living on an island and we are in a crisis,\\u201d he said. It'll be the decisions coming out of this that are really important and offset the temporary pain we\\u2019re feeling - Bell Bay Aluminium general manager Ray Mostogl He said he\\u00a0wants to see a long term solution to the state\\u2019s power woes. \\u201cIt\\u2019ll be the decisions coming out of this that are really important and offset the temporary pain we\\u2019re feeling.\\u201d The company receives no financial benefit from reducing its load, other than not paying for the power saved. Energy Minister Matthew Groom also faced the inquiry, and said the energy situation was an extreme weather event. Mr Groom said if inflows were equal to previous lows, the current storage levels would be 8 per cent higher. He described the energy crisis as a \\u201cwake up call\\u201d when it came\\u00a0to understanding climate change. Other major users Temco, Nyrstar, and Norske\\u00a0Skog have also reduced energy consumption."
    pp = pre_process("punctuation.txt", "stopwords.txt")
    terms = pp.text_process(text)
    print terms
    terms_k = pp.phrase_process(text)
    print terms_k
    print [w for w in terms if w not in terms_k]
