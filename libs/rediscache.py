import redis 
import os
from datetime import datetime 
from libs import logs   

REDIS_URL = os.getenv('REDIS_URL','')
REDIS_CONN = None 

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue="DEBUG",
            flaskapp=None)


if (REDIS_URL != ''):
    REDIS_CONN = redis.from_url(REDIS_URL)
    REDIS_CONN.set('key','value')
    REDIS_CONN.expire('key', 300) # 5 minutes
    logger.info("{}  - Initialization done Redis" .format(datetime.now()))

def __display_RedisContent():
    for keys in REDIS_CONN.scan_iter():
        logger.info(keys)
    cacheData = __getCache('keys *')
    if cacheData != None:
        for entry in cacheData:
            logger.info(entry)




def __setCache(key, data, ttl):
    if (REDIS_CONN != None):
        logger.info('Storing in Redis')
        REDIS_CONN.set(key, data)
        REDIS_CONN.expire(key, ttl)



def __getCache(key):
    if (REDIS_CONN != None):
        logger.info('Reading in Redis')
        return REDIS_CONN.get(key)
    return None 