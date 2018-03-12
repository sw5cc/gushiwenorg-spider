# -*- coding: utf-8 -*-

import redis
import logging


logger = logging.getLogger(__name__)


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
COOKIE_DB = 1
GUSHIWEN_URL = 'http://www.gushiwen.org'


def get_new_cookie():
    try:     
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=COOKIE_DB)
    except:
        logger.error("connect redis failed")
    else:
        try:
            s = requests.Session()
            response = s.post(GUSHIWEN_URL)
        except:
            pass
        else:
            cookies = response.cookies.get_dict()
            return json.dumps(cookies)
