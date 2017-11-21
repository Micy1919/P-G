# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import redis
import argparse
from flask import Flask
from flask import request
from flask import make_response
from topnews_config import get_config

parser = argparse.ArgumentParser()
parser.add_argument("--nation", dest='nation', default='None', type=str)
parser.add_argument("--lan", dest='lan', default='None', type=str)
args = parser.parse_args()

if args.nation == 'None' or args.lan == 'None':
    raise NameError
nation = args.nation
lan = args.lan
top_config = get_config({'nation': nation, 'lan': lan})

app = Flask(__name__)
redis_cli = redis.StrictRedis(host=top_config['REDIS_SERVER'], port=top_config['REDIS_PORT'], db=0)
redis_cli_in = redis.StrictRedis(host=top_config['REDIS_SERVER'], port=6379, db=0)


@app.route('/allnews', methods=['GET'])
def get_all_news():
    country = request.args.get('country')
    language = request.args.get('language')
    print request
    print country, language
    if country == 'in' and language == 'en':
        TN_ALL = '{}_TNEWS_ALL_V0'.format(country)
        resp_r = redis_cli_in.get(TN_ALL)
        resp_j = json.loads(resp_r)
        resp_s = []
        
        for item in sorted(resp_j, key=lambda x: x['ttl'], reverse=True):
            if len(resp_s) >= top_config['NEWS_MAX']:
                break
            else:
                resp_s.append(item)
        resp = json.dumps(resp_s)
    elif country == 'pk' and language == 'ur':
        TN_ALL = '{}_TNEWS_ALL_V0_{}_{}_'.format(country, country, language)
        resp_r = redis_cli.get(TN_ALL)
        resp_j = json.loads(resp_r)
        resp_s = []

        for item in sorted(resp_j, key=lambda x: x['ttl'], reverse=True):
            if len(resp_s) >= top_config['NEWS_MAX']:
                break
            else:
                resp_s.append(item)
        resp = json.dumps(resp_s)
    elif country == 'bd' and language == 'bn':
        TN_ALL = '{}_TNEWS_ALL_V0_{}_{}_'.format(country, country, language)
        resp_r = redis_cli.get(TN_ALL)
        resp_j = json.loads(resp_r)
        resp_s = []

        for item in sorted(resp_j, key=lambda x: x['ttl'], reverse=True):
            if len(resp_s) >= top_config['NEWS_MAX']:
                break
            else:
                resp_s.append(item)
        resp = json.dumps(resp_s)
    elif country == 'id' and language == 'id':
        TN_ALL = '{}_TNEWS_ALL_V0_{}_{}_'.format(country, country, language)
        resp_r = redis_cli.get(TN_ALL)
        resp_j = json.loads(resp_r)
        resp_s = []

        for item in sorted(resp_j, key=lambda x: x['ttl'], reverse=True):
            if len(resp_s) >= top_config['NEWS_MAX']:
                break
            else:
                resp_s.append(item)
        resp = json.dumps(resp_s)
    else:
        resp = '[]'

    print resp
    response = make_response(resp)
    response.mimetype = 'application/json'
    return response


@app.route('/delete', methods=['POST'])
def delete_news():
    entry_id = request.args.get('entry_id')
    country = request.args.get('country')
    language = request.args.get('language')
    if country == 'in' and language == 'en':
        TN_ALL = '{}_TNEWS_ALL_V0'.format(country, country, language)
        data = json.loads(redis_cli.get(TN_ALL))
        left = []
        for news in data:
            if news['entry_id'] == entry_id:
                continue
            else:
                left.append(news)

        redis_cli.set(TN_ALL, json.dumps(left))
        TN_DEL = 'TNEWS_DEL'
        del_row = redis_cli_in.get(TN_DEL)
        print del_row
        if del_row != None:
            del_list = json.loads(del_row)
        else:
            del_list = []
        del_list.append(entry_id)
        redis_cli.set(TN_DEL, json.dumps(del_list))

        resp = 'ok'
    elif country == 'pk' and language == 'ur':
        TN_ALL = '{}_TNEWS_ALL_V0_{}_{}_'.format(country, country, language)
        data = json.loads(redis_cli.get(TN_ALL))
        left = []
        for news in data:
            if news['entry_id'] == entry_id:
                continue
            else:
                left.append(news)

        redis_cli.set(TN_ALL, json.dumps(left))
        TN_DEL = 'TNEWS_DEL_{}_{}_'.format(country, language)
        del_row = redis_cli.get(TN_DEL)
        print del_row
        if del_row != None:
            del_list = json.loads(del_row)
        else:
            del_list = []
        del_list.append(entry_id)
        redis_cli.set(TN_DEL, json.dumps(del_list))

        resp = 'ok'
    elif country == 'bd' and language == 'bn':
        TN_ALL = '{}_TNEWS_ALL_V0_{}_{}_'.format(country, country, language)
        data = json.loads(redis_cli.get(TN_ALL))
        left = []
        for news in data:
            if news['entry_id'] == entry_id:
                continue
            else:
                left.append(news)

        redis_cli.set(TN_ALL, json.dumps(left))
        TN_DEL = 'TNEWS_DEL_{}_{}_'.format(country, language)
        del_row = redis_cli.get(TN_DEL)
        print del_row
        if del_row != None:
            del_list = json.loads(del_row)
        else:
            del_list = []
        del_list.append(entry_id)
        redis_cli.set(TN_DEL, json.dumps(del_list))

        resp = 'ok'
    elif country == 'id' and language == 'id':
        TN_ALL = '{}_TNEWS_ALL_V0_{}_{}_'.format(country, country, language)
        data = json.loads(redis_cli.get(TN_ALL))
        left = []
        for news in data:
            if news['entry_id'] == entry_id:
                continue
            else:
                left.append(news)

        redis_cli.set(TN_ALL, json.dumps(left))
        TN_DEL = 'TNEWS_DEL_{}_{}_'.format(country, language)
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
    app.run(host='0.0.0.0', port=9002)
