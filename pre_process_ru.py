# -*- coding: utf-8 -*-
from coda.tokenizer import Tokenizer
from coda.disambiguator import Disambiguator
from coda.syntax_parser import SyntaxParser
import time
import nltk

dic = {}
tokenizer = Tokenizer("RU")
disambiguator = Disambiguator("RU")

class DotDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.__dict__ = self

    def allow_dotting(self, state=True):
        if state:
            self.__dict__ = self
        else:
            self.__dict__ = dict()


class pre_process(object):
    def __init__(self, punctuation_file, stopwords_file, special_terms=["_line_"]):
        self.punctuation = set([line.strip() for line in open(punctuation_file, "r")])
        self.stopwords = set([line.strip() for line in open(stopwords_file, "r")])
        self.special_terms = special_terms
        self.__tokens = None
        self.__content = []
        self.grammars = ["NP: {<N.*>}", "NP: {<A|N.*><N.*>}", "NP: {<N.*><IN|N.*><N.*>}"]

    def __to_unicode(self,input_str):
        """
        确定编码
        :param input_str:
        :return:
        """
        if isinstance(input_str, str):
            return unicode(input_str, encoding="utf-8", errors='ignore')
        else:
            return input_str

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
        self.__tokens = tokenizer.tokenize(text)

    def __del_stopwords(self):
        """
        去除停用词。
        :param terms: 单词列表
        :return:
        """
        self.__content = [term for term in self.__content if term[0] not in self.stopwords]

    def __stem(self, ):
        """
        词干化。
        :param terms: 单词列表
        :return:
        """
        disambiguated = disambiguator.disambiguate(self.__tokens)
        for item in disambiguated:
            self.__content.append((item.lemma,item.label.split('@')[0],item.content))

    def __get_noun_chunks(self):
        """
        得到名词组合
        :return:
        """
        tagged_words = [(w[2],w[0]) for w in self.__content]
        noun_chunks = []
        for grammar in self.grammars:
            cp = nltk.RegexpParser(grammar)
            result = cp.parse(tagged_words)
            NP = [list(kt) for kt in result if not isinstance(kt, tuple)]
            NP = [" ".join([w for w, _ in np]) for np in NP]
            noun_chunks += NP
        return noun_chunks

    def __get_ents(self):
        """
        得到实体词
        :return:
        """
        return []


    def text_process(self, text):
        """
        文本预处理。
        :param text: 文本, string
        :return:
        """
        self.__content = []
        text = self.__del_punctution(self.__del_special_terms(text.lower()))
        if text.strip() == '':
            return []
        self.__tokenize(text)
        self.__stem()
        self.__del_stopwords()
        #terms = self.__stem(self.__is_local_for_text(terms))
        return [w[0] for w in self.__content]

    def __call__(self, text):
        """
        关键词接口
        :param text:
        :return:
        """
        self.__content = []
        text = self.__del_punctution(self.__del_special_terms(text.lower()))
        if text.strip() == '':
            return []
        self.__tokenize(text)
        self.__stem()
        term = DotDict()
        term.allow_dotting()
        term.noun_chunks = self.__get_noun_chunks()
        term.ents = self.__get_ents()




if __name__ == '__main__':
    pp = pre_process("punctuation.txt", "stopwords.txt")
    start_time = time.time()
    text = u'МИД пригрозил ограничить поездки американских дипломатов по России.'
    print pp.text_process(text)
    doc = pp(text)
    print doc.noun_chunks




