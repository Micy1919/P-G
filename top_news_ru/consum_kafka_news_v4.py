# -*- coding:utf-8 -*-
import time
import json
import redis
import logging
import argparse
import datetime
import requests
import traceback
#from time import time
import kafka_config as config
from datetime import timedelta
from kafka import KafkaConsumer
from topnews_config import get_config
from sklearn.metrics.pairwise import cosine_similarity


parser = argparse.ArgumentParser()
parser.add_argument("--nation", dest='nation', default='None', type=str)
parser.add_argument("--lan", dest='lan', default='None', type=str)
parser.add_argument("--ntype", dest='ntype', default='None', type=str)
parser.add_argument("--fport", dest='fport', default='5000', type=str)
args = parser.parse_args()

if args.nation == 'None' or args.lan == 'None' or args.ntype == 'None' or args.fport == 'None':
    raise NameError
nation = args.nation
ntype = args.ntype
lan = args.lan
fport = args.fport
top_config = get_config({'nation': nation, 'lan': lan, 'port': fport})

MOST_COUNT = 1
valud_duration = 3600 * 1 * 6

redis_cli = redis.StrictRedis(host=top_config['REDIS_SERVER'], port=top_config['REDIS_PORT'], db=0)
# 上线的话去掉注释
redis_cli_prod = redis.StrictRedis(host=top_config['PROD_SERVER'], port=top_config['PROD_PORT'], db=0)
current_key = top_config['PROD_KEY'] + '{}_{}'.format(nation, lan)

ban_urls = ['www.ligaolahraga.com/jadwal-bola']

logging.basicConfig(filename='logger_%s.log'% (ntype), level=logging.INFO)


class NewsStreamingConsumer:
    def __init__(self, nation):
        group_id = ('topnews_client_%s_%s' % (nation, ntype))
        if nation == 'us' or nation == 'id':
            config_sever_key = ('%s_new' % nation)
        else:
            config_sever_key = ('%s_new' % 'in')
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
                        if not language or language != lan:
                            continue

                        no_of_pictures = news_storage.get('no_of_pictures', 0)
                        if not no_of_pictures > 0:
                            continue

                        title = news_storage.get('title', '')
                        if not title:
                            continue

                        if len(title) > top_config['MAX_TITLE'] or len(title) < top_config['MIN_TITLE']:
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
    """
    判断是否失效，失效时间是1小时
    :param timestamp_str:
    :return:
    """
    expire_date = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=valud_duration)
    if expire_date < datetime.datetime.utcnow():
        return True

    return False

def cookkafkaresult(processed_set):
    for entry_id in processed_set:
        line = processed_set[entry_id]
        news = json.loads(line)

        while True:
            res = requests.post(top_config['API'], data=line)
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
                if score > top_config['NN_SCORE']:
                    index_news = redis_cli.get(nation + top_config['TN_ALL'])
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

                        old = redis_cli.get(top_config['TN_PRE'] + entry_id)
                        if old == None:
                            print 'empty news'
                            continue

                        old_j = json.loads(old)
                        old_f = old_j['feature']
                        dist = cosine_similarity([feature], [old_f])
                        if dist[0] > top_config['SIM_SCORE']:
                            if isoutofdate(raw_ts):
                                rerun = True
                            else:
                                print 'same news'
                                continue

                        next_list.append(tn)

                    del_news = redis_cli.get(nation + top_config['TN_DEL'])
                    if del_news != None:
                        del_list = json.loads(del_news)
                    else:
                        del_list = []

                    if not rerun and news['entry_id'] not in del_list:
                        find = {}
                        find['entry_id'] = news['entry_id']
                        find['ttl'] = now + 3600 * top_config['STAY_HOUR']
                        next_list.append(find)

                        redis_cli.set(top_config['TN_PRE'] + news['entry_id'], json.dumps(d2v))
                        redis_cli.set(nation + top_config['TN_ALL'], json.dumps(next_list))
                        all_top = redis_cli.get(nation + top_config['TN_ALL'])
                        print all_top
                        print len(json.loads(all_top))

                        prod_list = []
                        for item in sorted(next_list, key=lambda x: x['ttl'], reverse=True):
                            if len(prod_list) > top_config['NEWS_MAX']:
                                break
                            info = {}
                            info['status'] = 0
                            info['entry_id'] = item['entry_id']
                            prod_list.append(info)
                        # 正式上线时候取消下面的注释
                        redis_cli_prod.set(current_key, json.dumps(prod_list))
                        print 'key is {} and list is {}'.format(current_key, prod_list)
                        print 'done for publish'

if __name__ == '__main__':
    top_domains = set()
    with open('data/top_domains_v4.tsv') as lines:
        for line in lines:
            domain = line.strip()
            top_domains.add(domain)

    consumer = NewsStreamingConsumer(nation)
    processed_set = {}
    begin_time = time.time()
    for s in range(1):#consumer.get_news_streaming:
        now_time = time.time()
        if now_time - begin_time < 60 * 30:
            begin_time = now_time
            print 'backfill'
            for line in open('./data/storage_all_id_break.tsv'):
                news = json.loads(line.strip())
                if 'url' not in news:
                    news['url'] = 'backfill_url'
                processed_set[news['entry_id']] = json.dumps(news)

        if len(processed_set) >= MOST_COUNT:
            cookkafkaresult(processed_set)
            processed_set = {}