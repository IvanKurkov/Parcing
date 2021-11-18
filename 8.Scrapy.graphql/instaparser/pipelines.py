# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy

from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client['instagram']

    def process_item(self, item, spider):
        item['_id'] = f"{item['my_user_id']}{item['partition']}{item['other_user_id']}"

        collections = self.mongo_base["friendships"]

        collections.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item


class ProfilePhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            yield scrapy.Request(item['other_user_photo'])
        except Exception as e:
            print(e)

    def item_completed(self, results, item, info):
        item['other_user_photo'] = [itm[1] for itm in results if itm[0]]
        return item
