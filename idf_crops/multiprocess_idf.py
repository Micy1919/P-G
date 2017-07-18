# -*- coding:utf-8 -*-
"""
用多进程多方式去处理语料，计算语料的idf值
"""
import time
import multiprocessing
import pickle
from pre_process import pre_process

def func_crops(crops_list, pre_pro, file_name):
    print 'begin:',fime_name
    word_dic = {}
    for route in crops_list:
        with open(route, 'r') as f:
            for line in f:
                line = line.strip().replace('false', '0').replace('true', '1').replace('null', 'None')
                try:
                    mid_dic = eval(line)
                    language = mid_dic['language'].lower()
                    if 'en' in language:
                        mid_word = set(pre_pro.text_process(mid_dic['content']))
                        for w in mid_word:
                            if w in word_dic:
                                word_dic[w] = word_dic[w] + 1
                            else:
                                word_dic[w] = 1
                except:
                    continue
    pickle.dump(word_dic, open('./idf/'+file_name, 'w'))


def func(crops_list,file_name):
    time.sleep(3)
    print time.ctime()
    pickle.dump(crops_list, open('./idf/' + file_name, 'w'))


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=3)
    routelist = pickle.load(open('./saved/routelist.p', 'r'))
    split_list = [routelist[i:i+200000] for i in range(len(routelist)) if i%200000 == 0]
    for i in range(len(split_list)):
        fime_name = 'idf_'+str(i)
        pool.apply_async(func_crops, (split_list[i],pre_process(), fime_name))
    pool.close()
    pool.join()