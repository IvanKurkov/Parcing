import sys
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.instagram_followers import InstagramFollowersSpider
from instaparser.spiders.instagram_following import InstagramFollowingSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramFollowersSpider)
    process.crawl(InstagramFollowingSpider)
    process.start()

