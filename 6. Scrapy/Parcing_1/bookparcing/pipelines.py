# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class BookparcingPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client['Books']

    def process_item(self, item, spider):
        collections = self.mongo_base[spider.name]
        collections.update_one({'url': item['url']}, {'$set': item}, upsert=True)
        return item
