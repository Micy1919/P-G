# -*- coding:utf-8 -*-
"""
train_model and deal crops
"""
import config
config.set_language('en')
lan = config.get_language()
import time
import pickle
import random
import numpy as np
from lucene import initVM
initVM()
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.cross_validation import cross_val_score
from supervised_keywords_server import SupervisedKeyowrds
from model_evaluation import cal_precision_and_recall

SAMPLE_FILE = 'data/en/train_data_0207.pkl' #us
#SAMPLE_FILE = 'data/id/train_data_id_4715_0213.pkl'#0124
bxz_all = 0
bxz_select = 0
def deal_crops(train, weight = 1):
    global bxz_all, bxz_select
    features = train['features']
    all_candidates = train['all_candidates']
    golde_set_keywords = train['golden_set_keywords']
    ### add keywords weight

    label = [0 for _ in range(len(all_candidates))]
    positive_index = []
    for i in range(len(golde_set_keywords)):
        bxz_all += 1
        if golde_set_keywords[i] in all_candidates:
            bxz_select += 1
            p_index = all_candidates.index(golde_set_keywords[i])
            positive_index.append(p_index)
            word_weight = int((len(golde_set_keywords) - i) * weight)
            label = label[:] + [1 for j in range(word_weight)]
            for j in range(word_weight):
                features = np.vstack((features, features[p_index][:]))
        else:
            positive_index.append(None)
    for i in positive_index:
        if i is None:
            continue
        label[i] = 1
    return np.array(label), features


def get_train_features_labels(data, weight):
    all_labels = None
    all_features = None
    cnt_of_doc = 0
    for doc_idx in data:
        labels, features = deal_crops(data[doc_idx], weight)
        if cnt_of_doc == 0:
            all_labels = labels
        else:
            all_labels = np.concatenate((all_labels, labels))
        if cnt_of_doc == 0:
            all_features = features
        else:
            all_features = np.vstack((all_features, features))

        cnt_of_doc += 1
    print 'finally select:', bxz_select/float(bxz_all)
    return {'features': all_features, 'labels': all_labels}


def train_model_from_all_corpus(classifier_type):

    train_data = pickle.load(open(SAMPLE_FILE, 'r'))
    print 'train_data:', len(train_data)
    train_XY = get_train_features_labels(train_data)

    # train model for keyword classification
    if classifier_type == 'logistic':
        model = LogisticRegression()
        model = model.fit(train_XY['features'], train_XY['labels'])
        pickle.dump(model, open('data/logisticregression.pkl', 'wb'))
    elif classifier_type == 'random forest':
        model = RandomForestClassifier(n_estimators=1000)
        model = model.fit(train_XY['features'], train_XY['labels'])
        pickle.dump(model, open('data/randomforest.pkl', 'wb'))
    elif classifier_type == 'gbdt':
        model = GradientBoostingClassifier(n_estimators=1000)
        model = model.fit(train_XY['features'], train_XY['labels'])
        pickle.dump(model, open('data/'+lan+'/gbdt.pkl', 'wb'))

    '''validate the testdata for this model'''
    in_sample_acc = cross_val_score(model, train_XY['features'], train_XY['labels'], cv=4)
    print 'In-sample cross-validated accuracy: %.4f' % in_sample_acc.mean()


def five_fold_inner_compare(classifier_type, weight):
    alldata = pickle.load(open(SAMPLE_FILE, 'r'))
    all_doc_id = alldata.keys()

    FLOD_RATIO = 5
    mean_score = []
    for iter_idx in range(FLOD_RATIO):
        print 'five_fold.....', iter_idx
        selected_doc_id = random.sample(all_doc_id, len(all_doc_id) / FLOD_RATIO)
        print 'this iter we select test sample:', len(selected_doc_id)
        testdata = {i: alldata[i] for i in selected_doc_id}
        traindata = {i: alldata[i] for i in all_doc_id if i not in selected_doc_id}
        print 'traindata:', len(traindata)
        train_XY = get_train_features_labels(traindata, weight)

        model = None
        if classifier_type == 'logistic':
            model = LogisticRegression()
            model = model.fit(train_XY['features'], train_XY['labels'])
        elif classifier_type == 'random forest':
            model = RandomForestClassifier(n_estimators=1000)
            model = model.fit(train_XY['features'], train_XY['labels'])
        elif classifier_type == 'gbdt':
            model = GradientBoostingClassifier(n_estimators=1000)
            model = model.fit(train_XY['features'], train_XY['labels'])

        supervised_model = SupervisedKeyowrds(model)
        for test in testdata.keys():
            content = testdata[test]['content']
            title = testdata[test]['title']
            url = testdata[test]['url']
            supervised_keywords = supervised_model.extract_keywords(content, title, url, 5)
            print supervised_keywords
            supervised_keywords = sorted(supervised_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
            testdata[test]['supervised_keywords'] = [i[0] for i in supervised_keywords]
            print testdata[test]['supervised_keywords']
        mean_score.append(cal_precision_and_recall(testdata))

    # experiment score output
    mean_score_pr = {}
    for idx in range(len(mean_score)):
        for k in mean_score[idx]:
            if k not in mean_score_pr:
                mean_score_pr[k] = mean_score[idx][k]
            else:
                mean_score_pr[k][0] += mean_score[idx][k][0]
                mean_score_pr[k][1] += mean_score[idx][k][1]
    print '..........................................................\n'
    print 'last result:', weight
    for i in mean_score_pr:
        print i, mean_score_pr[i][0] / 5.0, mean_score_pr[i][1] / 5.0


def compare(model):
    supervised_model = SupervisedKeyowrds(model)
    testdata = pickle.load(open(SAMPLE_FILE, 'r'))
    for test in testdata:
        content = testdata[test]['content']
        title = testdata[test]['title']
        url = testdata[test]['url']
        supervised_keywords = supervised_model.extract_keywords(content, title, url, 5)
        #print supervised_keywords
        supervised_keywords = sorted(supervised_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
        testdata[test]['supervised_keywords'] = [i[0] for i in supervised_keywords]
        print testdata[test]['supervised_keywords']
    print cal_precision_and_recall(testdata)


def main():
    t1 = time.time()
    #train_model_from_all_corpus('gbdt')
    t2 = time.time()
    print 'totally cost time:', (t2 - t1) / 60
    weight = [0.2, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
    for w in weight:

      five_fold_inner_compare('gbdt', w)
    #model = pickle.load(open('data/gbdt_us.pkl', 'rb'))
    #compare(model)

if __name__ == '__main__':
    main()

