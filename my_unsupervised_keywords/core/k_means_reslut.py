# -*- coding:utf-8 -*-
"""
把结果取word2vec 然后得到的向量结果进行分类，取每一类的weight最大值作为最终结果
"""
import numpy as np
from gensim.models import KeyedVectors
from sklearn.cluster import KMeans,AffinityPropagation


class KMeansResult():

    def __init__(self, model = None , topK= 5):
        if model is None:
            self.model = KeyedVectors.load_word2vec_format(
                'data/en/GoogleNews-vectors-negative300.bin.gz', binary=True)
            self.k_means = KMeans(init='k-means++', n_clusters=topK, n_init=10)
        else:
            self.model = model
            self.k_means = KMeans(init='k-means++', n_clusters=topK, n_init=10)

    def get_words_vec(self, words, dimension = 300):
        word_vec = np.zeros(dimension)
        no_leng = 0
        for w  in words.split():
            if w in self.model:
                word_vec += self.model[w]
            else:
                no_leng += 1
        if (word_vec == np.zeros(dimension)).all():
            return False
        return word_vec/float(len(words.split()) - no_leng)

    def get_candidates_vec(self,candidates):
        print 'begin build word2vec'
        word_vec = None
        num_label = 0
        for word in candidates:
            token_vec = self.get_words_vec(candidates[word]['origin_word'])
            if token_vec is False:
                candidates[word]['k_means'] = 'Zeros'
                continue
            candidates[word]['k_means'] = num_label
            num_label += 1
            token_vec.shape = (300, 1)
            token_vec = np.transpose(token_vec)
            if word_vec is None:
                word_vec = token_vec
            else:
                word_vec = np.vstack((word_vec, token_vec))
        return word_vec,candidates


    def k_means_result(self, candidates):
        X, candidates = self.get_candidates_vec(candidates)
        print X.shape
        y_labels = list(self.k_means.fit(X).labels_)
        for word in candidates:
            if candidates[word]['k_means'] == 'Zeros':continue
            candidates[word]['k_means'] = y_labels[candidates[word]['k_means']]
        return candidates

