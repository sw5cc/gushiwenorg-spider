# -*- coding: utf-8 -*-

import requests
import json
from gushiwen_master.settings import PROXY_SHADOWSOCKS_ONLY, SHADOWSOCKS_SCHEME, SHADOWSOCKS_SERVER, SHADOWSOCKS_PORT

def get_http_proxies():
    proxies = []
    if PROXY_SHADOWSOCKS_ONLY:
        proxies.append(SHADOWSOCKS_SCHEME+'://'+SHADOWSOCKS_SERVER+':'+str(SHADOWSOCKS_PORT))
    else:
        try:
            r = requests.get('http://127.0.0.1:10010/?types=0&count=10&country=国内')
            ip_ports = json.loads(r.text)
            for ip in ip_ports:
                proxies.append('http://'+str(ip[0])+':'+str(ip[1]))
        except:
            proxies = []        
    return proxies


def removekey(d, key):
    r = dict(d)
    if key in r:
        del r[key]
    return r
