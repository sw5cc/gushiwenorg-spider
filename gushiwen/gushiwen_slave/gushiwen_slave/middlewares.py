# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import base64
import random
import logging

from urllib.parse import urlparse
from scrapy.exceptions import IgnoreRequest, CloseSpider, NotConfigured
from scrapy.http import Request
from six.moves.urllib.request import getproxies, proxy_bypass
from urllib.request import _parse_proxy
from six.moves.urllib.parse import urlunparse
from scrapy.utils.httpobj import urlparse_cached
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.downloadtimeout import DownloadTimeoutMiddleware
from gushiwen_slave.user_agent import USER_AGENTS
from gushiwen_slave.utils.proxy_helper import get_http_proxies
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.utils.response import response_status_message
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.python import global_object_name


logger = logging.getLogger(__name__)


class GushiwenSlaveSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GushiwenSlaveDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GushiwenUserAgentMiddleware(object):
    """
    downloadermiddlewares
    This middleware allows spiders to override the user_agent
    """

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings['USER_AGENT'])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, 'user_agent', self.user_agent)

    def process_request(self, request, spider):
        ua = self._user_agent(spider)
        if ua:
            request.headers.setdefault(b'User-Agent', ua)    

    def _user_agent(self, spider):
        ua = getattr(spider, 'user_agent', self.user_agent)
        if ua:
            return ua
        else:
            return random.choice(USER_AGENTS)


class GushiwenHttpProxyMiddleware(object):
    '''
    downloadermiddlewares
    '''
    global count

    logger = logger


    def __init__(self, auth_encoding='latin-1'):
        global count
        self.auth_encoding = auth_encoding
        count = 1
        self._update_proxies()


    def _update_proxies(self):
        self.proxies = [[None, None]]
        # skip system proxy
        for type, url in getproxies().items():
            creds, proxy_url = self._get_proxy(url, type)
            if type in ('http', 'https'):               
                self.proxies.append([creds, proxy_url])
        for url in get_http_proxies():
            self.proxies.append([None, url])
        logger.debug('Update proxy list {0}'.format(self.proxies))


    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING')
        return cls(auth_encoding)


    def _basic_auth_header(self, username, password):
        user_pass = to_bytes(
            '%s:%s' % (unquote(username), unquote(password)),
            encoding=self.auth_encoding)
        return base64.b64encode(user_pass).strip()


    def _get_proxy(self, url, orig_type):
        proxy_type, user, password, hostport = _parse_proxy(url)
        proxy_url = urlunparse((proxy_type or orig_type, hostport, '', '', '', ''))

        if user:
            creds = self._basic_auth_header(user, password)
        else:
            creds = None

        return creds, proxy_url


    def process_request(self, request, spider):
        # update proxies
        global count
        count+=1
        if count % 100 == 0:
            count = 1
            self._update_proxies()

        if 'direct_connect' in request.meta:                
            value = request.meta['direct_connect']
            del request.meta['direct_connect']
            if value:
                if 'proxy' in request.meta:
                    del request.meta['proxy']
                logger.debug('HTTP_PROXY-->Direct')
                return

        # change proxy
        if 'proxy' in request.meta:
            proxy_url = None
            creds = None
            if request.meta['proxy'] is None:
                self._set_proxy(request)
                return
            else:
                creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
            request.meta['proxy'] = proxy_url
            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = b'Basic ' + creds
            return
        elif not self.proxies:
            # local ip
            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        # 'no_proxy' is only supported by http schemes
        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return

        # add proxy
        self._set_proxy(request)


    def _set_proxy(self, request):
        creds, proxy = self.proxies[random.randint(0, len(self.proxies)-1)]
        if proxy:
            request.meta['proxy'] = proxy
            logger.debug('HTTP_PROXY-->Proxy {0}'.format(proxy))
        else:
            if 'proxy' in request.meta:
                del request.meta['proxy']
            logger.debug('HTTP_PROXY-->Direct')
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic ' + creds


class GushiwenRetryMiddleware(object):

    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            if retries == retry_times-1:
                retryreq.meta['direct_connect'] = True
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})


class GushiwenRedirectMiddleware(object):

    def process_response(self, request, response, spider):
        code = response.status
        # Redirect
        if code == 302:
            retryreq = request.copy()
            retryreq.meta['direct_connect'] = True
            return retryreq.replace(dont_filter=True)
        else:
            return response