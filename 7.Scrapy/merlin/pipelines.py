# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import hashlib
from scrapy.utils.python import to_bytes
from pymongo import MongoClient


class MerlinPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client['merlen']

    def process_item(self, item, spider):
        item['params_dict'] = dict(zip(item['params_name'], item['params_value']))
        del item['params_name']
        del item['params_value']

        collections = self.mongo_base[spider.name]
        collections.update_one({'url': item['url']}, {'$set': item}, upsert=True)

        return item


class MerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{item["name"]}/full/img{image_guid}.jpg'
