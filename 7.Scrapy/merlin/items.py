# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst




def process_price(value:str):
    try:
        value = float(value)
    except Exception as e:
        print(e)
    finally:
        return value

def process_param_value(value:str):
    value = value.replace('\n', '').strip()
    return value

class MerlinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    params_name = scrapy.Field()
    params_value = scrapy.Field(input_processor=MapCompose(process_param_value))
    params_dict = scrapy.Field()
    _id = scrapy.Field()