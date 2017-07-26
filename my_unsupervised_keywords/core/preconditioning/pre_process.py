# -*- coding:utf-8 -*-
__author__ = 'chenjun'

from nltk.stem.porter import PorterStemmer


class PreProcess(object):
    def __init__(self, punctuation_file, stopwords_file, common_words_file, special_terms_file):
        self.punctuation = set([line.strip() for line in open(punctuation_file, "r")])
        self.stopwords = set([line.strip() for line in open(stopwords_file, "r")])
        self.special_terms = set([line.strip() for line in open(special_terms_file, "r")])
        self.common_words = set([line.strip() for line in open(common_words_file, "r")])

    def __del_special_terms(self, text):
        """
        删除指定特殊字符。
        :param text: 文本
        :return:
        """
        for s_term in self.special_terms:
            text = text.replace(s_term, ". ")
        return text

    def __del_punctution(self, text):
        """
        删除标点符号。
        :param text: 文本
        :return:
        """
        special = [("'s", " is"), ("'m", " am"), ("'re", " are"), ("'ve", " have"), ("'t", " not"), ("'ll", " will"), ("'d", " had")]
        for old, new in special:
            text = text.replace(old, new)
        for punct in self.punctuation:
            text = text.replace(punct, " ")
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

    def __num_ratio(self, term, ratio):
        count = 0.
        flag = False
        for t in term:
            if self.__is_number(t):
                count += 1
        if count / len(term) > ratio:
            flag = True
        return flag

    def __is_local_for_text(self, terms, ratio):
        """
        判断文本单词中是否是存在非local字符，如存在去除单词。
        :param terms: 单词
        :param ratio: 比率
        :return:
        """
        words = []
        for term in terms:
            flag = True
            term = term.decode("utf8")
            for w in term:
                if not (self.__is_alphabet(w) or self.__is_number(w)):
                    flag = False
                    break
            if term in self.common_words or self.__num_ratio(term, ratio):
                flag = False
            if flag:
                words.append(term)
        return words

    def __is_local_for_phrase(self, terms, ratio):
        """
        判断候选短语单词中是否存在非local字符或者常用词， 如存在，则舍弃短语。
        :param terms: 候选短语单词
        :param ratio: 比率
        :return:
        """
        flag = True
        for term in terms:
            term = term.decode("utf8")
            for w in term:
                if not (self.__is_alphabet(w) or self.__is_number(w)):
                    flag = False
                    break
            if term in self.common_words or self.__num_ratio(term, ratio):
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
        terms = self.__stem(self.__is_local_for_phrase(terms, ratio=0.6))
        return terms

    def text_process(self, text):
        """
        文本预处理。
        :param text: 文本, string
        :return:
        """
        text = self.__del_punctution(self.__del_special_terms(text.lower()))
        terms = self.__del_stopwords(self.__tokenize(text))
        terms = self.__stem(self.__is_local_for_text(terms, ratio=0.6))
        return terms


if __name__ == "__main__":
    text = "India vs 333,22 Australia: Ravichandran Ashwin breaks Dale Steyn\u2019s record of most wickets in a Test season_line_ddddd six 7s 777s"
    #path = "/Users/chenjun/PycharmProjects/KeyWords/pre_process/"
    path = ''
    pp = PreProcess(path+"punctuation.txt", path+"stopwords.txt", path+"common_words.txt", path+"special_terms.txt")
    terms = pp.text_process(text)
    print terms
    terms = pp.phrase_process(text)
    print terms