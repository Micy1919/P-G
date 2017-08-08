# -*- coding:utf-8 -*-
import json
import codecs
import math

def judge_num(text):
    try:
        token = int(text)
        return True
    except:
        return False

idf_dict = {}
f = codecs.open('./corpus_by_category.txt', 'r').readlines()
content_num = len(f)
num = 0
for doc in f:
    if num%10000 == 0:
        print num
    num += 1
    doc = doc.strip().decode('utf-8')
    word = set(doc.split())
    for w in word:
        if judge_num(w):continue
        if w in idf_dict:
            idf_dict[w] = idf_dict[w] + 1
        else:
            idf_dict[w] = 1
for doc in idf_dict:
    idf_dict[doc] = math.log10(float(content_num)/float(idf_dict[w]))

json.dump(idf_dict, open('idf_slim.json', 'w'))