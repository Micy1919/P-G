# -*- coding: utf-8 -*-
from coda.tokenizer import Tokenizer
from coda.disambiguator import Disambiguator
from coda.syntax_parser import SyntaxParser
import time

dic = {}
tokenizer = Tokenizer("RU")
disambiguator = Disambiguator("RU")

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
        #text = text.replace("'s", " is")
        #text = text.replace("'m", " am")
        #text = text.replace("'re", " are")
        #text = text.replace("'ve", " have")
        for punct in self.punctuation:
            text = text.replace(punct.decode('utf-8'), u"")
        return text
    
    def __del_number(self, text):
        for num in '0123456789':
            text = text.replace(num.decode('utf-8'), u"")
        return text

    def __tokenize(self, text):
        """
        按空格分词。
        :param text: 文本
        :return:
        """
        tokens = tokenizer.tokenize(text)
        return tokens

    def __del_stopwords(self, terms):
        """
        去除停用词。
        :param terms: 单词列表
        :return:
        """
        terms = [term for term in terms if term not in self.stopwords]
        return terms

    def __stem(self, tokens):
        """
        词干化。
        :param terms: 单词列表
        :return:
        """
        terms = []
        disambiguated = disambiguator.disambiguate(tokens)
        for item in disambiguated:
            print (item.lemma,item.label)
            lemma = self.__del_number(item.lemma)
            terms.append(lemma)
            if lemma not in dic:
                dic[lemma] = set()
            dic[lemma].add(self.__del_number(item.content))
        return terms

    def text_process(self, text):
        """
        文本预处理。
        :param text: 文本, string
        :return:
        """
        text = self.__del_punctution(self.__del_special_terms(text.lower()))
        if text.strip() == '':
            return []
        terms = self.__stem(self.__tokenize(text))
        terms = self.__del_stopwords(terms)
        #terms = self.__stem(self.__is_local_for_text(terms))
        return terms

if __name__ == '__main__':
    pp = pre_process("punctuation.txt", "stopwords.txt")
    start_time = time.time()
    print pp.text_process(u'МИД пригрозил ограничить поездки американских дипломатов по России.')




