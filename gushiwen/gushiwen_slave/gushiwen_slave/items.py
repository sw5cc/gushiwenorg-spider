# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GushiwenItem(scrapy.Item):
    mongodb_id = scrapy.Field()
    author = scrapy.Field()
    dynasty = scrapy.Field()
    tag = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()
    original_url = scrapy.Field()
    good = scrapy.Field()

