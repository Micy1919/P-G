#encoding='utf-8'

import sys
from polyglot.text import Text 

def convert_entity_list(list_tags, list_words):
    length = len(list_tags)
    res = {}

    for cnt in range(0,length):
        mark = True
        tag = list_tags[cnt]
        word = list_words[cnt]

        if cnt != 0:
           word_pre = list_words[cnt-1]
           if word in word_pre and word != word_pre:
              mark = False
        if cnt != length -1 :
           word_next = list_words[cnt+1]
           if word in word_next and word != word_next:
              mark = False

        if mark == False:
           continue
        s = tag+" "+word
        if res.has_key(s):
           res[s] += 1
        else:
           res[s] = 1

    return res

def get_key1(content, all_dict):
    res = {}
    length = len(content)
    front_length = int(0.3 * length)
    front_text = content[0:front_length]
    for key,value in all_dict.iteritems():
        word = key[6:]
        try :
           if front_text.find(word) == -1:
              continue
        except:
           print word
           continue
        res[key] = value
    return res

def get_key2(content, key_dict):
    if len(key_dict) == 0:
       return key_dict

    res = {}

    max_times = 0
    for key,value in key_dict.iteritems():
        max_times = max(max_times,value)
        
    if max_times >= 2 :
       for key,value in key_dict.iteritems():
           if value >= 2:       
              res[key] = value
    else:
       first_word = ""
       first_index = len(content)
       for key,value in key_dict.iteritems():
           word = key[6:]
           index = content.find(word)
           if index < first_index:
              first_word = key
              first_index = index
       res[first_word] = 1
           
    return res
    

class key_entity_predictor:
     def predict_all(self, content):
         content = Text(content)
         list_tags = []
         list_words = []
         for sent in content.sentences:
           for entity in sent.entities:
               tag = entity.tag
               word = " ".join(entity)
               list_tags.append(tag)
               list_words.append(word)
         all_dict = convert_entity_list(list_tags, list_words)
         return all_dict


     def predict_key(self, content):
         content = Text(content)
         list_tags = []
         list_words = []
         for sent in content.sentences:
           for entity in sent.entities:
               tag = entity.tag
               word = " ".join(entity)
               list_tags.append(tag)
               list_words.append(word)
         all_dict = convert_entity_list(list_tags, list_words)
         key_dict = get_key1(content,all_dict)
         key_dict = get_key2(content,key_dict)
         return key_dict


