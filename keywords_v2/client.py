# -*- coding: utf-8 -*-
import thriftpy
import gflags
import sys

supervised_keywords_thrift = thriftpy.load("keywords_v2.thrift", module_name="keywords_v2_thrift")

from thriftpy.rpc import make_client
from keywords_v2_thrift import *

def print_keyword_list(keywords):
  sorted_keywords = sorted(keywords, key=lambda x: x.score, reverse=True)
  for keyword in sorted_keywords:
    print keyword.term, keyword.score

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
  news.title = '''The List of Executive Orders that Trump Will Dispose of Immediately'''
  news.main_content ='''Barack Obama has spent years using his authoritative pen to sign executive orders into law because Congress constantly prevented him from approving his particular set of rules. To date, Obama has singed 235 executive orders dealing with every issue from climate change to national security.\nThe interesting thing about executive orders is that they are built on faulty foundations. They are more theoretical than factual. An executive order can be ripped out from under itself just as quickly as it was signed. \nOn day one of his presidency, Donald Trump will be able to shred and dispose of any executive order that Obama signed into law, making them 100 percent invalid. \nHere is a list of orders we can expect to see Trump handle immediately:\nClimate change- The Paris Agreement, EPA regulations, Clean Power Plan\nTrade- North American Free Trade Agreement (NAFTA), Trans-Pacific Partnership (TPP) Negotiations\nHealth Care- Any order that supports Obamacare (a program that Congress has to repeal)\nImmigration- Deferred Action for Childhood Arrivals program (DACA)\nNational Security- Ensuring Lawful Interrogations, Iran Sanctions\nYou can also expect to see any miscellaneous regulations involving the economy, gun sales, and technology restrictions to be abolished.\nNeedless to say, the Obama administration, which was built on a faulty executive overreach foundation, will quickly come crashing down. Arrogantly, Obama will try and persuade Trump from eliminating his executive orders when they meet at the White House on Thursday. \n
  '''

  while True:
    client = make_client(supervised_keywords_thrift.SupervisedKeyword, host, port)
    for i in range(10):
      print i
      request = FindKeywordsRequest(news, 10)
      response = client.find_keywords(request)
    client.close()
    print response
  #print_keyword_list(response.keywords)
