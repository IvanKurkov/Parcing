# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    my_username = scrapy.Field()
    my_user_id = scrapy.Field()
    _id = scrapy.Field()
    other_user_photo = scrapy.Field()
    other_user_fullname = scrapy.Field()
    other_username = scrapy.Field()
    other_user_id = scrapy.Field()
    partition = scrapy.Field()


