import scrapy
from scrapy.http import HtmlResponse
from bookparcing.items import BookparcingItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D1%84%D0%B0%D0%BD%D1%82%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%B0/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@title="Следующая"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@class="cover"]/@href').getall()
        for i in links:
            yield response.follow(i, callback=self.book_pars)

    def book_pars(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').get()
        author = response.xpath('//a[@data-event-label="author"]/text()').get()
        price = response.xpath('//span[@class="buying-priceold-val-number"]/text()').get()
        price_new = response.xpath('//span[@class="buying-pricenew-val-number"]/text()').get()
        rate = response.xpath('//div[@id="rate"]/text()').get()
        url = response.url
        yield BookparcingItem(name=name, author=author, price=price, price_new=price_new, rate=rate, url=url)