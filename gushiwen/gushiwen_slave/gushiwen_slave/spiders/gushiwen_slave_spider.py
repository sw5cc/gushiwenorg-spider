# -*- coding: utf-8 -*-


from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy.http import Request
from gushiwen_slave.utils.result_parse import list_first_item, clean_url, strip_nl, good_to_int
from gushiwen_slave.items import GushiwenItem


class GushiwenMasterSpider(RedisSpider):
    name = 'gushiwen_slave'
    redis_key = 'slave:requests'

    def parse(self, response):
        gushiwen = GushiwenItem()
        response_selector = Selector(response)
        gushiwen['title'] = list_first_item(response_selector.xpath('//div[@class="sons"]//h1/text()').extract())
        dynasty = response_selector.xpath('//div[@class="sons"]//p[@class="source"]//a/text()').extract()
        gushiwen['dynasty'] = dynasty[0]
        gushiwen['author'] = dynasty[1]
        conp = response_selector.xpath('//div[@class="sons"][1]//div[@class="contson"]/p/text()').extract()
        cont = response_selector.xpath('//div[@class="sons"][1]//div[@class="contson"]/text()').extract()
        if len(conp) >= len(cont):
            content =  conp
        else:
            content =  cont
        gushiwen['content'] = content
        gushiwen['tag'] = strip_nl(response_selector.xpath('//div[@class="sons"][1]//div[@class="tag"]//text()').extract())
        good = response_selector.xpath('//div[@class="sons"][1]//div[@class="good"]/a')
        gushiwen['good'] = list_first_item(good_to_int(good.xpath('string(.)').extract()))
        gushiwen['original_url'] = response.url
        yield gushiwen
    
