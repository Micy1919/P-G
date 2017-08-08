#-*- coding:utf-8 -*-
import argparse
import thriftpy
from keywords_server import Keywords
from thriftpy.rpc import make_server
from thriftpy.utils import serialize
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("--port", dest='port', default=6040, help='port of service', type=int)
args = parser.parse_args()

keywords_v2_thrift = thriftpy.load("keywords_v2.thrift", module_name="keywords_v2_thrift")
from keywords_v2_thrift import *

STOP_FILE = './data/en/stopwords_en.txt'
PUN_FILE = './data/en/punctuation.txt'
COMMON_WORDS_FILE = './data/en/common_words_en.txt'
SPECIAL_FILE = './data/en/special_words_en.txt'

class Dispatcher(object):

  def __init__(self,):
      self.root_predictor = Keywords(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE, 'en')

  def find_keywords(self, request):
      """

      :param request:
      :return:
      """
      try:
          start = datetime.now()
          content, title, url, topK = request.news.main_content, request.news.title, request.news.url, request.topK
          #print content,title
          result = self.root_predictor.top_keywords_news(title, content, topK)
          keyword_list = [Keyword(k, v) for k, v in result.items()]
          duration = datetime.now() - start
          print "find similar keywords total duration:", duration.total_seconds(), "nid:", request.news.nid
          return FindKeywordsResponse(keyword_list)
      except Exception as Inst:
          print datetime.now(), "failed to find similar keywords", request.news.nid
          print "error is:", Inst
          return FindKeywordsResponse([])
def main():
    server = make_server(keywords_v2_thrift.Keywords_v2, Dispatcher(),
                         '0.0.0.0', args.port)
    server.trans.client_timeout = None
    server.serve()


if __name__ == '__main__':
    main()
