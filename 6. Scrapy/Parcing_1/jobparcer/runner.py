from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparcer.spiders.hhru import HhruSpider
from jobparcer.spiders.sjru import SjruSpider
from jobparcer import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SjruSpider)
    process.start()
#scrapy crawl hhru