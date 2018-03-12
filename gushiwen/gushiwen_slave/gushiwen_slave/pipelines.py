# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import datetime
import traceback
import logging
from pprint import pprint
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class GushiwenSlavePipeline(object):
    def process_item(self, item, spider):
        return item


class SingleMongodbPipeline(object):
    """
        save the data to mongodb.
    """

    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 10086
    MONGODB_DB = "gushiwen_fs"

    logger = logger

    def __init__(self):
        """
            The only async framework that PyMongo fully supports is Gevent.
            
            Currently there is no great way to use PyMongo in conjunction with Tornado or Twisted. PyMongo provides built-in connection pooling, so some of the benefits of those frameworks can be achieved just by writing multi-threaded code that shares a MongoClient.
        """
        
        try:
            client = MongoClient(self.MONGODB_SERVER,self.MONGODB_PORT) 
            self.db = client[self.MONGODB_DB]
        except Exception as e:
            print("ERROR(SingleMongodbPipeline): %s"%(str(e),))
            traceback.print_exc()

    @classmethod
    def from_crawler(cls, crawler):
        cls.MONGODB_SERVER = crawler.settings.get('MONGODB_SERVER', 'localhost')
        cls.MONGODB_PORT = crawler.settings.getint('MONGODB_PORT', 10086)
        cls.MONGODB_DB = crawler.settings.get('MONGODB_DB', 'gushiwen_fs')
        pipe = cls()
        pipe.crawler = crawler
        return pipe

    def process_item(self, item, spider):
        gushiwen_detail = {
            'author':item.get('author'),
            'dynasty':item.get('dynasty'),
            'tag':item.get('tag',[]),
            'content':item.get('content',[]),
            'title':item.get('title',''),
            'original_url':item.get('original_url',''),
            'good':item.get('good', 0),
            'update_time':datetime.datetime.utcnow(),
        }
        
        result = self.db['gushiwen_detail'].insert(gushiwen_detail)
        item["mongodb_id"] = str(result)

        self.logger.debug("Item %s wrote to MongoDB database %s/gushiwen_detail" %
                    (result, self.MONGODB_DB))
        return item
