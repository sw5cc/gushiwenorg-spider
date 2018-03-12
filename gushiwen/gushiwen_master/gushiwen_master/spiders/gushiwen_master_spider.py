# -*- coding: utf-8 -*-


from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy.http import Request
from gushiwen_master.utils.result_parse import list_first_item, clean_url, strip_nl, next_author
from gushiwen_master.utils.insert_redis import insert_start_url, insert_request


class GushiwenMasterSpider(RedisSpider):
    name = 'gushiwen_master'
    redis_key = 'master:start_urls'

    def parse(self, response):
        response_selector = Selector(response)
        next_link = list_first_item(response_selector.xpath('//div[@class="pages"]/a[text()="下一页"]/@href').extract())
        main3 = response_selector.xpath('//div[@class="main3"]').extract()

        if next_link:
            next_link = clean_url(response.url, next_link)
            insert_start_url(next_link)
            # yield Request(url=next_link, callback=self.parse)
        elif main3:
            next_link = next_author(response.url)
            insert_start_url(next_link)
            # yield Request(url=next_link, callback=self.parse)

        # # FIXME: slow
        for detail_link in response.xpath('//div[@class="cont"]//p//@href').extract():  
            if detail_link.find('/shiwenv_') != -1:
                detail_link = clean_url(response.url, detail_link)
                insert_request(detail_link)            
