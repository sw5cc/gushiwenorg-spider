# -*- coding: utf-8 -*-

import redis
import logging


logger = logging.getLogger(__name__)


REDIS_HOST = 'localhost'
REDIS_PORT = 6379


def insert_start_url(arg):
    try:     
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    except:
        logger.error("connect redis failed")
    else:
        r.lpush('master:start_urls', arg)


def insert_request(arg):
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    except:
        logger.error("connect redis failed")
    else:
        r.lpush('slave:requests', arg)
