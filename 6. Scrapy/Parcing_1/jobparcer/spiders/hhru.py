import scrapy
from scrapy.http import HtmlResponse
from jobparcer.items import JobparcerItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?fromSearchLine=true&text=Python&area=1&search_field=description&search_field=company_name&search_field=name',
                  'https://hh.ru/search/vacancy?fromSearchLine=true&text=Python&area=2&search_field=description&search_field=company_name&search_field=name']

    def parse(self, response: HtmlResponse):
        next_p = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_p:
            yield response.follow(next_p, callback=self.parse)

        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_pars)

    def vacancy_pars(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//div[@class='vacancy-salary']/span/text()").getall()
        url = response.url
        yield JobparcerItem(name=name, salary=salary, url=url)
