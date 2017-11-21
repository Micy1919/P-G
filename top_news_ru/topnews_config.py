# -*- coding:utf-8 -*-
"""
kafka的读取设置
"""


def get_config(kwargs):
    """
    :param kwargs:
    :return:
    """
    nation = kwargs.get('nation', '')
    lan = kwargs.get('lan', '')
    flask_port = kwargs.get('port', '5000')
    if not nation or not lan:
        raise ValueError
    config = {
        'TN_PRE': 'TNEW_V0_{}_{}_'.format(nation, lan),
        'TN_DEL': 'TNEWS_DEL_{}_{}_'.format(nation, lan),
        'TN_ALL': '_TNEWS_ALL_V0_{}_{}_'.format(nation, lan),
        'REDIS_SERVER': 'localhost',
        'REDIS_PORT': 4444,
        'REBUILD_MIN': 30,
        'SIM_SCORE': 0.9,
        'NN': 100,
        'NN_SCORE': 3,
        'API': 'http://127.0.0.1:{}/topnews/{}'.format(flask_port, nation),
        'STAY_HOUR': 24,
        'NEWS_MAX': 50,
        'MAX_TITLE': 200,
        'MIN_TITLE': 10,
        'PROD_SERVER': '172.17.40.104',
        'PROD_PORT': 6666,
        'PROD_KEY': 'cms_top_news_list_',
    }
    return config
