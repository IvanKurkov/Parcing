# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparcingItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    price_new = scrapy.Field()
    rate = scrapy.Field()
    _id = scrapy.Field()


