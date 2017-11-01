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

MOST_COUNT = 50
valud_duration = 3600 * 72

nation = sys.argv[1]

storage_all_file_path = '/data01/cluster_in/kafka/storage_all_' + nation + '.tsv'
storage_all_file_path_tmp = '/data01/cluster_in/kafka/storage_all_' + nation + '_tmp.tsv'

ban_urls = ['www.ligaolahraga.com/jadwal-bola']

twitter_crawlers = ['twitter_influencers_crawler']

logging.basicConfig(filename='logger.log', level=logging.INFO)


class NewsStreamingConsumer:
    def __init__(self, nation):
        group_id = ('news_streaming_clustering_prime_%s' % nation)
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

                        title = news_storage.get('title', '')
                        if not title:
                            continue

                        content = news_storage.get('content', '')
                        if not content:
                            continue

                        timestamp = news_storage.get('timestamp', '')
                        if not timestamp:
                            continue

                        dup_flag = news_storage.get('dup_flag', '')

                        crawler_type = news_storage.get('crawler', '')

                        url = news_storage.get('url', '')
                        in_ban_url = False
                        for ban_url in ban_urls:
                            if ban_url in url:
                                in_ban_url = True

                        if in_ban_url:
                            continue

                        yield entry_id, title, content, timestamp, dup_flag, url, crawler_type, news_id
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
    with open(storage_all_file_path) as lines:
        for line in lines:
            line = line.strip()
            cols = line.split('\t', 4)
            if len(cols) < 5:
                continue
            if isoutofdate(cols[2]):
                continue
            entry_id = cols[0]
            if entry_id in processed_set:
                continue
            result.append(line)

    for entry_id in processed_set:
        result.append(processed_set[entry_id])

    savedStdout = sys.stdout
    with open(storage_all_file_path_tmp, 'w') as file:
        sys.stdout = file
        for line in result:
            print(line)

    sys.stdout = savedStdout
    os.rename(storage_all_file_path_tmp, storage_all_file_path)


if __name__ == '__main__':
    top_domains = set()
    with open('cooked_top_domains_in.tsv') as lines:
        for line in lines:
            domain = line.strip()
            top_domains.add(domain)

    consumer = NewsStreamingConsumer(nation)
    processed_set = {}
    for s in consumer.get_news_streaming:
        dup_flag = s[4]
        url = s[5]
        print(url)
        crawler_type = s[6]
        news_id = s[7]
        news_date = datetime.datetime.fromtimestamp(s[3]).strftime('%Y%m%d')
        news_time_str = datetime.datetime.fromtimestamp(s[3]).strftime('%Y-%m-%dT%H:%M:%SZ')
        if isoutofdate(news_time_str):
            continue

        in_top_domain = False
        for top_domain in top_domains:
            if top_domain in url:
                in_top_domain = True
                break

        if crawler_type.lower() not in twitter_crawlers and not in_top_domain:
            continue

        line = ('%s\t%s\t%s\t%s\t%s' % (
            s[0], news_id, news_time_str, s[1].replace('\n', ' '),
            s[2].replace('\n', 'NEWS_CLEAN|||NEWS_CLEAN'))).encode('utf-8')
        processed_set[s[0]] = line
        if len(processed_set) >= MOST_COUNT:
            cookkafkaresult(processed_set)
            processed_set = {}

