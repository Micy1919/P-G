# -*- coding:utf-8 -*-
"""
用redis去构建supervised_keyword_v2一些特征的抽取
"""
import redis


class RedisServer(object):

    def __init__(self, redis_config = None):
        if redis_config is None:
            self.__redis_config = {
                'host': '172.17.10.194',
                'port': 4444
            }
        else:
            self.__redis_config = redis_config
        self.__redis = self.establish_server()

    def establish_server(self):
        """
        建立redis的连接
        :return:
        """
        redis_cl = redis.Redis(self.__redis_config['host'], self.__redis_config['port'])
        return redis_cl

    def pre_key(self, key, pre='S'):
        """
        封装查询
        :return:
        """
        if not isinstance(key, str):
            key = key.encode('utf-8')
        return '{}:{}_in_en'.format(pre, key)

    def set(self, key, value):
        """
        添加数据
        :param key:
        :param value:
        :return:
        """
        key = self.pre_key(key)
        self.__redis.set(key, value)

    def mset(self, key_dict, pre='S'):
        """
        批量添加key的值
        :param key_dict:
        :param pre:
        :return:
        """
        token_dict = {
            self.pre_key(w, pre): key_dict[w]
            for w in key_dict
        }
        self.__redis.mset(token_dict)

    def get(self, key):
        """
        从redis里读取key的值
        :param key:
        :return:
        """
        input_key = self.pre_key(key)
        result = self.__redis.get(input_key)

        return result

    def mget(self, key_list, pre='S'):
        """
        批量得到数据
        :param key_list:
        :param pre:
        :return:
        [x1,x2,...] x1为str类型`
        """
        key_list = [self.pre_key(w, pre) for w in key_list]
        result = self.__redis.mget(key_list)

        return result

    def del_key(self, key, pre='S'):
        """
        删除key
        :param key:
        :param pre:
        :return:
        """
        key = self.pre_key(key, pre)
        self.__redis.delete(key)


if __name__ == '__main__':
    r = RedisServer()
    r.set('test_key', ['test_value_123456789qazwx1245', 98.1])
    result = r.get('test_key')
    print result
    r.del_key('test_key')
    result = r.get('test_key')
    print result
    print 'begin test mset and mget'
    test_dict = {
        'test1': ['1', 1],
        'test2': ['2', 2],
        'test3': ['3', 3]
    }
    r.mset(test_dict)
    result = r.mget(test_dict.keys())
    print result