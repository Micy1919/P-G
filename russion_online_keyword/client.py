# -*- coding: utf-8 -*-
import thriftpy
import gflags
import sys
import pickle
keywords_v2_thrift = thriftpy.load("keywords_v2.thrift", module_name="keywords_v2_thrift")

from thriftpy.rpc import make_client
from keywords_v2_thrift import *

def print_keyword_list(keywords):
  result = []
  for keyword in keywords.keywords:
    result.append((keyword.term, keyword.score))
  return result

if __name__ == '__main__':
  gflags.DEFINE_string("host", "0.0.0.0", "server host")
  gflags.DEFINE_integer("port", 6004, "server port")

  try:
     args = gflags.FLAGS(sys.argv)
  except gflags.FlagsError as err:
     print err
     sys.exit(err)

  host = gflags.FLAGS.host
  port = gflags.FLAGS.port

  print host, port

  news = News()

  news.url = "http://m.townhall.com/tipsheet/justinholcomb/2016/11/10/the-list-of-executive-orders-that-trump-will-dispose-of-immediately-n2243914"
  news.nid = "test_purpose_123456"
  news.title = '''The List of Executive Orders that Trump Will Dispose of Immediately'''
  news.main_content = '''Named entity recognition (NER) in Russian texts / Определение именованных сущностей (NER) в тексте на русском языке'''
  data = pickle.load(open('./ru_evlauation_36_0808.pkl','r'))
  client = make_client(keywords_v2_thrift.Keywords_v2, host, port)
  for doc in data:
    news.url = data[doc]['url']
    news.nid = str(doc)
    news.title = data[doc]['title']
    news.main_content = data[doc]['content']
    request = FindKeywordsRequest(news, 5)
    request = client.find_keywords(request)
    data[doc]['keyword'] = print_keyword_list(request)
  pickle.dump(data,open('./ru_evlauation_36_0808_.pkl','w'))#print_keyword_list(response.keywords)

