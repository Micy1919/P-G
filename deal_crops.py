# -*- coding:utf-8 -*-
"""
处理孟加拉从hive上爬取的语料
"""
import json
import datetime
from datetime import timedelta

data = open('./log_bd', 'r').readlines()
print 'we have data is {}'.format(len(data))

proccess_set = {}
for line in data:
    line = line.strip()
    l = line.split('\t')
    news = {}
    news['entry_id'] = l[0]
    news['news_id'] = l[1]
    news_date = datetime.datetime.fromtimestamp(l[2]).strftime('%Y%m%d')
    news_time_str = datetime.datetime.fromtimestamp(l[2]).strftime('%Y-%m-%dT%H:%M:%SZ')
    news['ts'] = news_time_str
    news['title'] = l[3]
    news['content'] = l[4].replace('_line_', '\n').decode('utf-8').encode('utf-8')
    news['push_source'] = l[5]
    news['domain'] = l[6]
    news['url'] = l[7]

    proccess_set[l[0]] = json.dumps(news)
with open('storage_all_file_path_tmp', 'w') as files:
    for line in proccess_set:
        files.write(line+'\n')