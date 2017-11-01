# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
import time
import traceback
import json
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from gensim.utils import tokenize
import threading
from flask import Flask
from flask import request
from flask import make_response
import redis
from topnews_config import *

app = Flask(__name__)
redis_cli = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

@app.route('/allnews', methods=['GET'])
def get_all_news():
    country = request.args.get('country')
    language = request.args.get('language')
    print country, language
    if country == 'in' and language == 'en':
        nation = 'in'
        resp_r = redis_cli.get(nation + TN_ALL)
        resp_j = json.loads(resp_r)
        resp_s = []
        
        for item in sorted(resp_j, key=lambda x: x['ttl'], reverse=True):
            if len(resp_s) >= NEWS_MAX:
                break
            else:
                resp_s.append(item)
        resp = json.dumps(resp_s)
    else:
        resp = '[]'

    response = make_response(resp)
    response.mimetype = 'application/json'
    return response

@app.route('/delete', methods=['POST'])
def delete_news():
    entry_id = request.args.get('entry_id')
    country = request.args.get('country')
    language = request.args.get('language')
    if country == 'in' and language == 'en':
        nation = 'in'
        data = json.loads(redis_cli.get(nation + TN_ALL))
        left = []
        for news in data:
            if news['entry_id'] == entry_id:
                continue
            else:
                left.append(news)

        redis_cli.set(nation + TN_ALL, json.dumps(left))
        
        del_row = redis_cli.get(TN_DEL)
        print del_row
        if del_row != None:
            del_list = json.loads(del_row)
        else:
            del_list = []
        del_list.append(entry_id)
        redis_cli.set(TN_DEL, json.dumps(del_list))
        
        resp = 'ok'
    else:
        resp = 'fail'

    return resp

from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001)
