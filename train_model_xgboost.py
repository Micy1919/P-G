# -*- coding:utf-8 -*-
"""
模型训练
"""
import matplotlib
matplotlib.use('Agg')
import os
import pickle
import codecs
import logging
import random
import argparse
import numpy as np
from datetime import datetime
from core.candidates.spacy_nlp import SpacyNlp
from core.candidates_word import CandidateKeyword
from sklearn.ensemble import GradientBoostingClassifier
import xgboost as xgb
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--dir", dest='dir', default='./data/en/', type=str)
args = parser.parse_args()
if not os.path.exists(args.dir):
    raise Exception('No this dir')
file_dir = args.dir
logging.basicConfig(filename = os.path.join(file_dir,'log.model'), level=logging.INFO)
logging.info('load data')
train_data = pickle.load(open(os.path.join(file_dir,'train_data.pkl'), 'r'))
test_data = pickle.load(open(os.path.join(file_dir,'test_data.pkl'), 'r'))
logging.info('successful load train_data: {}---test_data: {}'.format(len(train_data), len(test_data)))

logging.info('begin train model-------{}'.format(datetime.now()))
feature_dict = [
            'spacy',
            'ner',
            'noun',
            'title',
            'start',
            'last',
            'pharse',
            'num_ratio',
            'capit_ratio',
            'word_leng',
            'spread',
            'freq',
            'city',
            'cele',
            'tf',
            'tf_idf',
            'doc2',
            'doc2_max',
            'doc2_min',
            'doc2_avr',
            'doc2_word'
        ]
x_data = []
y_data = []
y_data_rank = []
all_pos = 0
train_group = []
for ent in train_data:
    user = train_data[ent]['global_pos']
    all_pos += len(user)
    token_group = 0
    for word in train_data[ent]['candidate_feature']:
        wf = train_data[ent]['candidate_feature'][word].__dict__
        token_x = [wf[feature_dict[i]] for i in range(len(feature_dict))]
        x_data.append(token_x[:])
        token_group += 1
        if word in user:
            y_data.append(1)
            y_data_rank.append(len(user) - user.index(word))
        else:
            y_data.append(0)
            y_data_rank.append(0)
    train_group.append(token_group)


x_test = []
y_test =[]
y_test_rank = []
test_group = []
test_all_pos = 0
test_model_pos = 0
for ent in test_data:
    user = test_data[ent]['global_pos']
    token_group = 0
    test_all_pos += len(user)
    for word in test_data[ent]['candidate_feature']:
        wf = test_data[ent]['candidate_feature'][word].__dict__
        token_x = [wf[feature_dict[i]] for i in range(len(feature_dict))]
        x_test.append(token_x[:])
        token_group += 1
        if word in user:
            test_model_pos += 1
            y_test.append(1)
            y_test_rank.append(len(user) - user.index(word))
        else:
            y_test.append(0)
            y_test_rank.append(0)
    test_group.append(token_group)


logging.info('finish x-y data and we have x_data:%s ; pos:%s ; all_pos:%s' % (str(len(y_data)), str(sum(y_data)), str(all_pos)))
logging.info('finsh x-y data and we have x_test:{}; pos:{}; pos_ratio:{}; all_pos:{}'.format(len(y_test), sum(y_test), float(test_model_pos)/test_all_pos, test_all_pos))
test_pos_ratio = float(test_model_pos)/test_all_pos

logging.info('sample candidate-------')
"""
sample 候选集
"""

x_data = np.array(x_data)
y_data = np.array(y_data)
y_data_rank = np.array(y_data_rank)
x_test = np.array(x_test)
y_test = np.array(y_test)
y_test_rank = np.array(y_test_rank)

#-----------------开始模型训练-------------#

model_0 = GradientBoostingClassifier(n_estimators=100)
"""
xgboost ranking
"""
dtrain = xgb.DMatrix(x_data, label=y_data_rank)
dtrain.set_group(train_group)
dtest = xgb.DMatrix(x_test, label=y_test_rank)
dtest.set_group(test_group)
"""
logging xgboost param
"""
param = {'objective': 'rank:pairwise',
         'eta': 0.1,
         'gamma': 1.0,
         'min_child_weight': 0.1,
         'num_round': 785,
         'max_depth': 5,
         'lambda': 0,
         'alpha': 0,
         'scale_pos_weight': 1}
watchlist = [(dtest, 'test'), (dtrain, 'train')]
logging.info('xgboost param {}'.format(param))


model_0 = model_0.fit(x_data, y_data)
model_1 = xgb.train(param, dtrain, param['num_round'], watchlist)

logging.info('save model GBDT and RANK')
#imodel_0.save_model(file_dir + '/gbdt.modle')
model_1.save_model(file_dir + '/ranking.modle')

predicted_prob_0 = model_0.predict_proba(x_test)
predicted_prob_0 = predicted_prob_0[:, 1]
predicted_prob_1 = model_1.predict(dtest)



precision_0, recall_0, thre_0 = precision_recall_curve(y_test, predicted_prob_0)
average_precision_0 = average_precision_score(y_test, predicted_prob_0)
precision_1, recall_1, thre_1 = precision_recall_curve(y_test, predicted_prob_1)
average_precision_1 = average_precision_score(y_test, predicted_prob_1)
logging.info('save pr data')
pr = {'GBDT':{}, 'RANK':{}}
pr['GBDT'] = {'precision':precision_0, 'recall':recall_0*test_pos_ratio, 'thresholds': thre_0}
pr['RANK'] = {'precision':precision_1, 'recall':recall_1*test_pos_ratio, 'thresholds': thre_1}
pickle.dump(pr, open(file_dir+'/pr.pkl','w'))

plt.figure(1)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title('2-class Precision-Recall model{}'.format('3-model'))

plt.plot(recall_0*test_pos_ratio, precision_0, color='b', label='%s--AP:%s' % ('GBDT', average_precision_0))
plt.plot(recall_1*test_pos_ratio, precision_1, color='r', label='%s--AP:%s' % ('RANK', average_precision_1))
plt.plot(0.155824508321, 0.48925, marker='*',  color='g', label='ONLINE')
logging.info('GBDT---AP----{}'.format(average_precision_0))
logging.info('Rank---AP----{}'.format(average_precision_1))

plt.legend()
plt.savefig(file_dir+'/2_model.png')

"""
def draw_bar(labels,quants):
    width = 0.4
    ind = np.linspace(0.5,len(feature_dict)+0.5,len(feature_dict))
    # make a square figure
    fig = plt.figure(2)
    ax  = fig.add_subplot(211)
    # Bar Plot
    ax.bar(ind-width/2,quants,width,color='green')
    # Set the ticks on x-axis
    ax.set_xticks(ind)
    ax.set_xticklabels(labels, rotation=90,fontsize=8)
    # labels
    ax.set_xlabel('feature')
    ax.set_ylabel('value')
    # title
    ax.set_title('Model Important', bbox={'facecolor':'0.8', 'pad':5})
    plt.grid(True)
    plt.savefig(file_dir+"/bar.png")

import_data = model_0.feature_importances_
import_data = [(import_data[i],feature_dict[i]) for i in range(len(import_data))]
import_data = sorted(import_data, key=lambda x:-x[0])
plt_x = [w[1] for w in import_data]
plt_y = [w[0] for w in import_data]
draw_bar(plt_x, plt_y)
"""

