import scrapy
from scrapy.http import HtmlResponse
from merlin.items import MerlinItem
from scrapy.loader import ItemLoader


class MerlinkatalogSpider(scrapy.Spider):

    name = 'merlinkatalog'
    allowed_domains = ['leroymerlin.ru']


    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


        links = response.xpath("//a[@data-qa='product-image']")

        for link in links:
            yield response.follow(link, callback=self.good_parse)

    def good_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=MerlinItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', '//uc-pdp-price-view[@class="primary-price"]/meta[@itemprop="price"]/@content')
        loader.add_xpath('photos', "//picture[@slot='pictures']/source[1]/@srcset")
        loader.add_xpath('params_name', "//dt[@class='def-list__term']/text()")
        loader.add_xpath('params_value', "//dd[@class='def-list__definition']/text()")
        loader.add_value('url', response.url)
        yield loader.load_item()