#-*- coding:utf-8 -*-
import pickle
import re

fhao_list =[u'[’!"#$%&\'()*+,-/:;<=>?，。?★、…【】《》？“”‘’！[\\]^_`{|}~\xa0]+',u'(_line_|“s|‘s|\'s)+']

def get_words(content):
    content = re.sub(fhao_list[0], ' ', content)
    return set(content.split())



def get_content_word_dic(routelist):
    word_dic = {}
    content_num = 0
    num = 0
    for route in routelist:
        num += 1
        if num%10000 == 0:
            print num,len(word_dic)
        with open(route, 'r') as f:
            for line in f:
                line = line.strip()
                line = line.replace('false', '0')
                line = line.replace('true', '1')
                line = line.replace('null', 'None')
                try:
                    mid_dic = eval(line)
                    language = mid_dic['language'].lower()
                    if 'en' in language:
                        content_num += 1
                        mid_word = get_words(mid_dic['content'])
                        for w in mid_word:
                            if w in word_dic:
                                word_dic[w] = word_dic[w] + 1
                            else:
                                word_dic[w] = 1
                except:
                    print 'read length error:'
    print 'all_content:',content_num
    pickle.dump(word_dic, open('en_0714.pkl', 'w'))

if __name__ == '__main__':
    routelist = pickle.load(open('./saved/routelist.p', 'r'))
    get_content_word_dic(routelist)
