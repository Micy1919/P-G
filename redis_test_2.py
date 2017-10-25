import redis
import pickle
from datetime import datetime
import time

redis_configs = {
        'id': ('172.17.40.227', 4444),
}

def get_all_keys(redis_cli, prefix):
    cursor = 0
    keys = []
    count = 0
    while True:
        count += 1
        scan_result = redis_cli.scan(cursor, prefix, 1000)
        #print scan_result
        cursor = scan_result[0]
        tmp_keys = scan_result[1]
        keys += tmp_keys
        if cursor == 0 or count > 10000000000:
            break

    print 'cursor times: %s' % count
    return keys

if __name__ == '__main__':
    for nation in redis_configs:
        print 'we use host {} and port {}'.format(redis_configs[nation][0], redis_configs[nation][1])
        r = redis.Redis(redis_configs[nation][0], redis_configs[nation][1])
        entry_ids = get_all_keys(r, 'S:*')
        print 'drop repaet'
        entry_ids = [w for w in entry_ids if 'in_en' in w]
        print 'we have news redis_indes is {}'.format(len(entry_ids))
        print 'stactis all keys ---- news'
        print entry_ids[:10]
        key_new = {}
        redis_num = 0
        for w in entry_ids:
            
            try:
                msg = r.get(w)
                msg = eval(msg)
                key_new[w] = int(msg[1])
            except:
                continue
            if redis_num % 10000 == 0:
                print redis_num
            redis_num += 1
        print 'done redis '
        top_k = 100
        print 'statis key top {}'.format(top_k)
        key_s = sorted(key_new.items(), key=lambda x: -x[1])
        print key_s[:top_k]
        key_num = [w[1] for w in key_s]
        print 'for all key max is {} and min is {} and avr is {} and mid is {}'.format(max(key_num), min(key_num), sum(key_num)/float(len(key_num)), key_num[(len(key_num)/2)])
        print 'zero num is {}'.format(len([w for w in key_num if w ==0]))
        
