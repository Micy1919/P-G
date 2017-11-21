import sys
import requests
import urllib2
import json
import traceback
cms_url = 'http://sg-socialdata-04-1-80.singa.op-mobile.opera.com/top/list'
detail_api = 'http://sg-socialdata-04-1-8080.singa.op-mobile.opera.com/in/news/entry_id/{0}'
trans_url = 'http://news-in.op-mobile.opera.com/news/detail/{0}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Cookie': 'operanews_token=lHNkmTluGhBO4eIhL7G0NHqHJP3bDlAyxow1jVQ%2BIVKqesl3nMCewUuJF8egANtETwfWisQ%2Fj3A%3D; JSESSIONID=C7D35DFF1C01AAAC4FB5FC8CC6B867FE; _ga=GA1.2.30749737.1505115649; _gid=GA1.2.204754780.1505115649'
}

import datetime
import time
def time_convert(ts):
    return datetime.datetime.fromtimestamp(
        int(ts)
    ).strftime('%Y-%m-%d %H:%M:%S')

db = {}
class News:
    def __init__(self, entry_id):
        self.entry_id = entry_id
        self.news_id = ''
        self.title = ''
        self.content = ''
        self.url = ''
        self.domain = ''
        self.ts = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False).encode('utf-8')

while True:
    r = requests.get(cms_url, headers=headers)
    response = r.content
    now = int(time.time())
    print '---------' + time_convert(now)
    for line in response.split('\n'):
        if 'ID =' in line:
            entry_id = line.split('=')[-1].split('<')[0].strip()
            if entry_id in db:
                continue

            try:
                news = News(entry_id)
                detail = urllib2.urlopen(detail_api.format(entry_id))
                data = json.loads(detail.read())
                news.title = data['title']
                news.domain = data['domain']
                news.url = data['url']
                news.content = data['content']
                news.news_id = data['id']
                news.ts = now

                db[entry_id] = news
                print entry_id, trans_url.format(news.news_id)
            except:
                print entry_id, traceback.format_exc()

    sw = open('db.txt', 'w')
    for k,v in db.items():
        sw.write('{0}\t{1}\n'.format(k, v.toJSON()))
    sw.close()

    print '---------done for {} news'.format(len(db))
    time.sleep(60*5)



