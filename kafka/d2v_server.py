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

logging.basicConfig(format='%(levelname)s [%(asctime)s] %(name)s - %(message)s', level=logging.INFO)

class TrainingSetLoader:
    def __init__(self, input_file):
        self.input_file = input_file

    def __iter__(self):
        for line in open(self.input_file):
            try:
                data = json.loads(line)
                id = data['news_id']
                content = data['content'].replace('\n', ' ')
                words = list(tokenize(content, lowercase=True))
                yield TaggedDocument(words=words, tags=[id])
            except Exception as e:
                logging.exception(e)
                logging.error('Row content: %s' % line)

class NewsDB:
    def __init__(self, country='in'):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.model = None
        self.thread.start()
        self.country = country
        self.redis_cli = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

    def run(self):
        while True:
            documents = TrainingSetLoader(sys.argv[1])
            new_model = Doc2Vec(documents=documents, size=100, iter=10,
                            min_count=5, window=15, dm=0, dbow_words=1,
                            hs=0, negative=5, workers=32, sample=1e-5)
            print '[DONE] update model'

            self.model = None
            index_news = self.redis_cli.get(self.country + TN_ALL)
            if index_news == None:
                index_news = '[]'
            current_list = json.loads(index_news)
            updated = 0
            for tn in current_list:
                entry_id = tn['entry_id']
                old = self.redis_cli.get(TN_PRE + entry_id)
                if old == None:
                    logging.warning('empty news {0}'.format(entry_id))
                    continue

                data = json.loads(old)
                content = data['content']
                test_text = list(tokenize(content, lowercase=True))
                inferred_vector_dm = new_model.infer_vector(test_text, steps=20, alpha=0.025)
                data['feature'] = inferred_vector_dm.tolist()
                self.redis_cli.set(TN_PRE + entry_id, json.dumps(data))
                updated += 1
            self.model = new_model
            print '[DONE] update {0} news'.format(updated)

            time.sleep(60 * REBUILD_MIN)

class Response:
    def __init__(self):
        self.feature = []
        self.sims = {}
        self.status = ''
        self.content = ''

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True)

app = Flask(__name__)
news_db_in = NewsDB('in')

def get_d2v(news_db):
    if request.method == 'POST':
        resp = Response()

        if news_db.model == None:
            resp.status = 'update'
        else:
            try:
                body = request.get_data()
                data = json.loads(body)
                content = data['content']
                resp.content = content
                resp.url = data.get('url', '')
                resp.title = data.get('title', '')
                resp.news_id = data.get('news_id', '')

                now = time.time()
                test_text = list(tokenize(content, lowercase=True))
                inferred_vector_dm = news_db.model.infer_vector(test_text, steps=20, alpha=0.025)
                sims = news_db.model.docvecs.most_similar([inferred_vector_dm], topn=NN)
                filtered = {}
                for id,dist in sims:
                    if dist > SIM_SCORE:
                        filtered[id] = dist

                resp.feature = inferred_vector_dm.tolist()
                resp.sims = filtered
                resp.status = 'success'

                latency = time.time() - now
                print latency
            except:
                logging.error(traceback.format_exc())
                resp.status = 'fail'

        response = make_response(resp.toJSON())
        response.mimetype = 'application/json'
        return response

@app.route('/topnews/in', methods=['POST'])
def get_news_in():
    return get_d2v(news_db_in)

from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
