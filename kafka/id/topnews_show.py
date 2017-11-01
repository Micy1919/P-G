# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from topnews_config import *
import redis
import time
import json

nation = 'in'
redis_cli = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

while True:
    all_top = redis_cli.get(nation + TN_ALL)
    to_show = {}

    for news in json.loads(all_top):
        entry_id = news['entry_id']
        key = TN_PRE + entry_id
        data = json.loads(redis_cli.get(key))

        url = data['url']
        title = data['title']
        content = data['content']
        summary = content[:min(500, len(content))]
        news_id = data['news_id']
        image_url = 'http://img.transcoder.opera.com/assets/v1/{0}'.format(news_id.split('_')[0])
        score = len(data['sims'])

        to_show[(url, title, summary, image_url)] = score

    print len(to_show)

    sw = open('show.html', 'w')

    for k,v in sorted(to_show.items(), key=lambda x: x[1], reverse=True):
        url, title, summary, image_url = k
        html = """\
        <html>
          <head></head>
          <body>
            <p>{4}<br>
            <a href="{3}">{0}</a><br>
            <img src="{2}" style="width:304px;height:228px;"><br>
              <table border="1">
                {1}
              </table>
            </p>
          </body>
        </html>
        """.format(title, summary, image_url, url, v)

        sw.write(html)

    sw.close()
    time.sleep(60*5)
