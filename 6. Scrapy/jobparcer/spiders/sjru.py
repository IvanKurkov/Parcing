import scrapy
from scrapy.http import HtmlResponse
from jobparcer.items import JobparcerItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a//span[contains(text(), 'Дальше')]/ancestor::a/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//a[contains(@class, "_6AfZ9")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_pars)

    def vacancy_pars(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//span[contains(@class, '_1OuF_ ZON4b')]/span/span/text()").getall()
        url = response.url
        yield JobparcerItem(name=name, salary=salary, url=url)
