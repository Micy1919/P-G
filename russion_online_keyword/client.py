# -*- coding: utf-8 -*-
import sys
sys.path.append('gen-py')

import gflags
from keywords import FindKeywords
from keywords.ttypes import *
import gflags

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def print_keyword_list(keywords):
  sorted_keywords = sorted(keywords, key=lambda x: x.weight)
  for keyword in sorted_keywords:
    print keyword.term, keyword.weight, keyword.origin_format

def print_entity_list(entities):
  sorted_entities = sorted(entities, key=lambda x: x.weight)
  for entity in sorted_entities:
    print entity.origin_format, "---", entity.stem_format, entity.weight, entity.origin_score

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
  '''
  news.url = "www.google.com"
  news.nid = "test_purpose_123456"
  news.title = 'this is a new york city news'
  news.main_content = u"Nahanni Fontaine\nSpecial adviser on Aboriginal women\u2019s issues for the government of Manitoba\nSagkeeng Anicinabe First Nation, lives in Winnipeg\nTo understand my journey, I must begin with my mother\u2019s story. \nMy maternal family is from the Sagkeeng First Nation, east of Winnipeg. My grandfather, Henry Charles Fontaine, was a Second World War veteran. After landing on the beaches of Normandy, he was captured by the Nazis, and spent nine months as a POW. Like most Aboriginal veterans, he was disenfranchised on his return to Canada. Soon after, he moved to Winnipeg to find work"
'''

  news.url = "http://m.townhall.com/tipsheet/justinholcomb/2016/11/10/the-list-of-executive-orders-that-trump-will-dispose-of-immediately-n2243914"
  news.nid = "test_purpose_123456"
  news.title = '''Named entity recognition (NER) in Russian texts / Определение именованных сущностей (NER) в тексте на русском языке'''
  news.main_content ='''Named entity recognition (NER) in Russian texts / Определение именованных сущностей (NER) в тексте на русском языке'''

  socket = TSocket.TSocket(host, port)
  transport = TTransport.TBufferedTransport(socket)
  protocol = TBinaryProtocol.TBinaryProtocol(transport)
  client = FindKeywords.Client(protocol)
  transport.open()

  result = client.find_keywords(news, 10)

  print "====== full keywords"
  print_keyword_list(result.full_keywords)

  print "====== title keywords"
  print_keyword_list(result.title_keywords)

  print "====== relevant entities"
  print_entity_list(result.relevant_entities)

  print "====== quality entities"
  print_entity_list(result.quality_entities)
  #print_keyword_list(response.keywords)
