# -*- coding:utf-8 -*-
"""
得到doc2vec的模型
"""
import pickle
import regex
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument


def regex_tokenizer(doc):
    """Return a function that split a string in sequence of tokens"""
    token_pattern = r"(?u)\b\w\w+\b"
    token_pattern = regex.compile(token_pattern)
    return token_pattern.findall(doc)


class TrainingSetLoader:
    def __init__(self, input_file):
        self.input_file = input_file

    def __iter__(self):
        for line in open(self.input_file):
            try:
                data = line.strip().split('\t')
                news_id = data[0]
                content = data[2].replace('_line_', ' ')
                words = list(regex_tokenizer(content))
                print news_id, '-----', content
                assert 1 == 2
                yield TaggedDocument(words=words, tags=[news_id])
            except Exception as e:
                assert 1==2
                print 'error ', e

documents = TrainingSetLoader('log_hi')
new_model = Doc2Vec(
    documents=documents,
    size=100, iter=10,
    min_count=5,
    window=15,
    dm=0,
    dbow_words=1,
    hs=0,
    negative=5,
    workers=32,
    sample=1e-5)
print '[DONE] update model'
pickle.dump(new_model, open('doc2_hi_model.pkl', 'w'))