import logging
import traceback
import json
from kafka import KafkaConsumer
import kafka_config as config
import datetime
from time import time
from datetime import timedelta
import sys
from sklearn.metrics.pairwise import cosine_similarity
import requests
from topnews_config import *
import redis
import time

nation = sys.argv[1]
ntype = sys.argv[2]

MOST_COUNT = 1
valud_duration = 3600 * 1

redis_cli = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
redis_cli_prod = redis.StrictRedis(host=PROD_SERVER, port=PROD_PORT, db=0)
current_key = PROD_KEY + 'test_test'
if nation == 'in':
    current_key = PROD_KEY + 'in_en'

ban_urls = ['www.ligaolahraga.com/jadwal-bola']

logging.basicConfig(filename='logger_%s.log'%(ntype), level=logging.INFO)

class NewsStreamingConsumer:
    def __init__(self, nation):
        group_id = ('topnews_client_%s_%s' % (nation, ntype))
        config_sever_key = ('%s_new' % nation)
        self._consumer = KafkaConsumer(config.KAFKA_TOPIC['new'],
                                       bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS[config_sever_key],
                                       group_id=group_id)

    @property
    def get_news_streaming(self):
        while True:
            try:
                for message in self._consumer:
                    value = json.loads(message.value)
                    if not value:
                        continue

                    try:
                        entry_id = value.get('entry_id', '')
                        if not entry_id:
                            continue
                        news_storage = value.get('news_storage', '')
                        if isinstance(news_storage, unicode):
                            news_storage = json.loads(news_storage)

                        news_id = news_storage.get('id', '')
                        if not news_id:
                            continue

                        country = news_storage.get('country', '')
                        if not country or country != nation:
                            continue

                        language = news_storage.get('language', '')
                        if not language or language != 'en':
                            continue

                        no_of_pictures = news_storage.get('no_of_pictures', 0)
                        if not no_of_pictures > 0:
                            continue

                        title = news_storage.get('title', '')
                        if not title:
                            continue

                        if len(title) > MAX_TITLE or len(title) < MIN_TITLE:
                            continue

                        if 'live' in title.lower().split(' '):
                            continue

                        content = news_storage.get('content', '')
                        if not content:
                            continue

                        timestamp = news_storage.get('timestamp', '')
                        if not timestamp:
                            continue

                        dup_flag = news_storage.get('dup_flag', '')

                        crawler_type = news_storage.get('crawler', '')
                        push_source = news_storage.get('push_source', '')
                        domain = news_storage.get('domain', '')
                        url = news_storage.get('url', '')
                        in_ban_url = False
                        for ban_url in ban_urls:
                            if ban_url in url:
                                in_ban_url = True

                        if in_ban_url:
                            continue

                        yield entry_id, title, content, timestamp, dup_flag, url, crawler_type, news_id, push_source, domain
                    except Exception as e:
                        logging.error('NewsStreamingConsumer: error: %s, %s', e.message, traceback.format_exc())
                        pass
            except Exception as e_outlayer:
                logging.info('consumer error: %s', e_outlayer.message)

def isoutofdate(timestamp_str):
    expire_date = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=valud_duration)
    if expire_date < datetime.datetime.utcnow():
        return True

    return False

def cookkafkaresult(processed_set):
    for entry_id in processed_set:
        line = processed_set[entry_id]
        news = json.loads(line)

        while True:
            res = requests.post(API, data=line)
            if res.status_code == 200:
                d2v = json.loads(res.content)
                print d2v['status']
                if d2v['status'] == 'success':
                    break
                else:
                    time.sleep(60)
            else:
                d2v = None
                print 'sever is down'
                time.sleep(60)
        
        if d2v:
            if d2v['status'] == 'success':
                now = int(time.time())
                score = len(d2v['sims'])
                feature = d2v['feature']
                rerun = False
                raw_ts = news['ts']
                print score
                if score > NN_SCORE:
                    index_news = redis_cli.get(nation + TN_ALL)
                    if index_news == None:
                        index_news = '[]'
                    current_list = json.loads(index_news)
                    next_list = []
                    for tn in current_list:
                        ttl = tn['ttl']
                        entry_id = tn['entry_id']
                        if ttl < now:
                            print 'old news'
                            continue

                        old = redis_cli.get(TN_PRE + entry_id)
                        if old == None:
                            print 'empty news'
                            continue

                        old_j = json.loads(old)
                        old_f = old_j['feature']
                        dist = cosine_similarity([feature], [old_f])
                        if dist[0] > SIM_SCORE:
                            if isoutofdate(raw_ts):
                                rerun = True
                            else:
                                print 'same news'
                                continue

                        next_list.append(tn)

                    del_news = redis_cli.get(nation + TN_DEL)
                    if del_news != None:
                        del_list = json.loads(del_news)
                    else:
                        del_list = []

                    if not rerun and news['entry_id'] not in del_list:
                        find = {}
                        find['entry_id'] = news['entry_id']
                        find['ttl'] = now + 3600 * STAY_HOUR
                        next_list.append(find)

                        redis_cli.set(TN_PRE + news['entry_id'], json.dumps(d2v))
                        redis_cli.set(nation + TN_ALL, json.dumps(next_list))
                        all_top = redis_cli.get(nation + TN_ALL)
                        print all_top
                        print len(json.loads(all_top))

                        prod_list = []
                        for item in sorted(next_list, key=lambda x: x['ttl'], reverse=True):
                            if len(prod_list) > NEWS_MAX:
                                break
                            info = {}
                            info['status'] = 0
                            info['entry_id'] = item['entry_id']
                            prod_list.append(info)
                        redis_cli_prod.set(current_key, json.dumps(prod_list))
                        print 'done for publish'

if __name__ == '__main__':
    top_domains = set()
    with open('top_domains_v4.tsv') as lines:
        for line in lines:
            domain = line.strip()
            top_domains.add(domain)

    consumer = NewsStreamingConsumer(nation)
    processed_set = {}
    begin_time = time.time()
    for s in consumer.get_news_streaming:
        dup_flag = s[4]
        url = s[5]
        print url
        crawler_type = s[6]
        push_source = s[8]
        domain = s[9]
        news_id = s[7]
        news_date = datetime.datetime.fromtimestamp(s[3]).strftime('%Y%m%d')
        news_time_str = datetime.datetime.fromtimestamp(s[3]).strftime('%Y-%m-%dT%H:%M:%SZ')
        if isoutofdate(news_time_str):
            continue

        is_keep = False
        is_top = False

        if ntype == 'client':
            if push_source == 'breaking-news':
                is_keep = True
            for top_domain in top_domains:
                if top_domain in url:
                    is_top = True
                    break
        elif ntype == 'top':
            for top_domain in top_domains:
                if top_domain in url:
                    is_top = True
                    is_keep = True
                    break
        elif ntype == 'all':
            is_keep = True
            is_top = True

        if not is_keep or not is_top:
            continue

        news = {}
        news['entry_id'] = s[0]
        news['news_id'] = news_id
        news['ts'] = news_time_str
        news['title'] = s[1]
        news['content'] = s[2].encode('utf-8')
        news['push_source'] = push_source
        news['domain'] = domain
        news['url'] = url

        processed_set[s[0]] = json.dumps(news)

        now_time = time.time()
        if now_time - begin_time > 60 * 30:
            begin_time = now_time
            print 'backfill'
            for line in open('storage_all_in_break.tsv'):
                news = json.loads(line.strip())
                if 'url' not in news:
                    news['url'] = 'backfill_url'
                processed_set[news['entry_id']] = json.dumps(news)

        if len(processed_set) >= MOST_COUNT:
            cookkafkaresult(processed_set)
            processed_set = {}
