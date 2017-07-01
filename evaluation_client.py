# -*- coding: utf-8 -*-
import sys
sys.path.append('gen-py')

import pickle
import gflags
from keywords import FindKeywords
from keywords.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def print_keyword_list(keywords):
  sorted_keywords = sorted(keywords, key=lambda x: x.weight)
  keywords_list = []
  for keyword in sorted_keywords:
    #print keyword.term, keyword.weight, keyword.origin_format
    keywords_list.append(keyword.origin_format)
    keywords_list.append(keyword.weight)
  return keywords_list

def print_entity_list(entities):
  sorted_entities = sorted(entities, key=lambda x: x.weight)
  for entity in sorted_entities:
    print entity.origin_format, "---", entity.stem_format, entity.weight, entity.origin_score

if __name__ == '__main__':
  gflags.DEFINE_string("host", "0.0.0.0", "server host")
  gflags.DEFINE_integer("port", 60110, "server port")
  try:
     args = gflags.FLAGS(sys.argv)
  except gflags.FlagsError as err:
     print err
     sys.exit(err)
  host = gflags.FLAGS.host
  port = gflags.FLAGS.port

  news = News()
  news.url = "www.google.com"
  news.nid = ""
  news.title = '''
  अखिलेश ने परिवारिक झगड़े से किया इंकार, बोले नेताजी हमारे साथ
'''
  news.main_content = '''
  शम्स तबरेज़, सियासत ब्यूरो।
   लखनऊ: अखिलेश यादव का कहना है कि मुलायम सिंह यादव की नाराजगी का कोई कारण नहीं है और साइकिल नेताजी की है। इसके लिए वे उनसे कई गुना चिंतित थे। अखिलेश ने भरोसे के साथ कहा कि मुलायम सिंह यादव साइकिल के लिए वोट मांगेंगे। अखिलेश ने परिवारिक झगड़े से भी इंकार किया है। अखिलेश ने ये भी कहा कि कोई नहीं जानता कि उनके पिता ने पार्टी का प्रचार न करने की बात किस सन्दर्भ में कही है।
    अखिलेश ने लखनऊ में एक कार्यक्रम के दौरान ये सारी बाते कही। उन्होने कहा कि सपा से जुड़ी ऐसी खबरें बढ़-चढ़कर लिखी जाती हैं। अलिखेश ने कहा कि नेताजी उनकी पार्टी के सबसे बड़े नेता हैं उनका आर्शीवाद उनके साथ है। उन्होने कहा कि मुलायम उनकी मदद करेंगे और नेता जी से उनकी बात होती रहती है।
  '''
  news.meta_keywords = [u'debate', u'first', u'hillary', u'clinton', u'donald', u'trump', u'lost', u'won', u'winner', u'highlights', u'summary', u'wrapup', u'trade', u'polls', u'election', u'iraq', u'isis', u'muslims']

  socket = TSocket.TSocket(host, port)
  transport = TTransport.TBufferedTransport(socket)
  protocol = TBinaryProtocol.TBinaryProtocol(transport)
  client = FindKeywords.Client(protocol)
  transport.open()
  evaluation_data = pickle.load(open('./evaluation_hindi.pkl','r'))
  for doc_id in evaluation_data:
    print doc_id
    news.url = evaluation_data[doc_id]['url'].encode('utf-8')
    news.title = evaluation_data[doc_id]['title'].encode('utf-8')
    news.main_content = evaluation_data[doc_id]['content'].encode('utf-8')
    result = client.find_keywords(news, 10)
    key_list = print_keyword_list(result.full_keywords)
    evaluation_data[doc_id]['keywords'] = key_list
  pickle.dump(evaluation_data, open('hindi_data.pkl','w'))

