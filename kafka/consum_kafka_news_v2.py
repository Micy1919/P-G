from __future__ import print_function
import logging
import traceback
import json
from kafka import KafkaConsumer
import kafka_config as config
import datetime
from time import time
from datetime import timedelta
import sys
import os
from topnews_config import *

nation = sys.argv[1]
ntype = sys.argv[2]

if ntype == 'break':
    MOST_COUNT = 1
    valud_duration = 3600 * 6
else:
    MOST_COUNT = 50
    valud_duration = 3600 * 72


storage_all_file_path = '/data01/cluster_in/kafka/storage_all_' + nation + '_' + ntype + '.tsv'
storage_all_file_path_tmp = '/data01/cluster_in/kafka/storage_all_' + nation + '_' + ntype + '_tmp.tsv'

ban_urls = ['www.ligaolahraga.com/jadwal-bola']

twitter_crawlers = ['twitter_influencers_crawler']

logging.basicConfig(filename='logger_%s.log'%(ntype), level=logging.INFO)


class NewsStreamingConsumer:
    def __init__(self, nation):
        group_id = ('news_streaming_clustering_prime_%s_%s' % (nation, ntype))
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

                        no_of_pictures = news_storage.get('no_of_pictures', 0)
                        if not no_of_pictures > 0:
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
    result = []
    if os.path.exists(storage_all_file_path):
        with open(storage_all_file_path) as lines:
            for line in lines:
                line = line.strip()
                data = json.loads(line)
                if isoutofdate(data['ts']):
                    continue
                entry_id = data['entry_id']
                if entry_id in processed_set:
                    continue
                result.append(line)

    for entry_id in processed_set:
        result.append(processed_set[entry_id])

    print('-------------total is %s' % (len(result)))
    #savedStdout = sys.stdout
    with open(storage_all_file_path_tmp, 'w') as files:
        #sys.stdout = file
        for line in result:
            #print(line)
            files.write(line+'\n')
    #sys.stdout = savedStdout
    os.rename(storage_all_file_path_tmp, storage_all_file_path)


if __name__ == '__main__':
    top_domains = set()
    with open('top_domains_v2.tsv') as lines:
        for line in lines:
            domain = line.strip()
            top_domains.add(domain)

    top_domains_less = set()
    with open('top_domains_v4.tsv') as lines:
        for line in lines:
            domain = line.strip()
            top_domains_less.add(domain)

    consumer = NewsStreamingConsumer(nation)
    processed_set = {}
    for s in consumer.get_news_streaming:
        dup_flag = s[4]
        url = s[5]
        print(url)
        crawler_type = s[6]
        push_source = s[8]
        domain = s[9]
        news_id = s[7]
        news_date = datetime.datetime.fromtimestamp(s[3]).strftime('%Y%m%d')
        news_time_str = datetime.datetime.fromtimestamp(s[3]).strftime('%Y-%m-%dT%H:%M:%SZ')
        if isoutofdate(news_time_str):
            continue
        '''
        in_top_domain = False
        for top_domain in top_domains:
            if top_domain in url:
                in_top_domain = True
                break

        if crawler_type.lower() not in twitter_crawlers and not in_top_domain:
            continue
        '''
        is_keep = False

        if ntype == 'break':
            if push_source == 'breaking-news':
                is_keep = True
                is_top = False
                for top_domain in top_domains_less:
                    if top_domain in url:
                        is_top = True
                        break
                is_keep = is_keep & is_top
        elif ntype == 'top':
            for top_domain in top_domains:
                if top_domain in url:
                    is_keep = True
                    break
        elif ntype == 'all':
            is_keep = True

        if not is_keep:
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
        #line = ('%s\t%s\t%s\t%s\t%s' % (
        #    s[0], news_id, news_time_str, s[1].replace('\n', ' '),
        #    s[2].replace('\n', 'NEWS_CLEAN|||NEWS_CLEAN'))).encode('utf-8')
        processed_set[s[0]] = json.dumps(news)
        if len(processed_set) >= MOST_COUNT:
            cookkafkaresult(processed_set)
            processed_set = {}
