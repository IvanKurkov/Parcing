# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re
import numpy as np
import json
import requests

cur_req = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
cur = json.loads(cur_req.text)


class JobparcerPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client['vacancy']

    @staticmethod
    def hh_salary(salary):
        min_salary = np.nan
        max_salary = np.nan
        if salary:
            salary = "".join(salary)

            salary = salary.replace("\xa0", "").replace(" ", "")

            if re.findall('от[0-9]+', salary) and re.findall('до[0-9]+', salary):
                min_salary = int(re.findall('[0-9]+', salary)[0])
                max_salary = int(re.findall('[0-9]+', salary)[1])
            elif re.findall('^от[0-9]+', salary):
                min_salary = int(re.findall('[0-9]+', salary)[0])
            elif re.findall('^до[0-9]+', salary):
                max_salary = int(re.findall('[0-9]+', salary)[0])

            if re.findall('[A-Z]', salary):
                currency = re.findall('[A-Z]{2,5}', salary)[0]
                if not np.isnan(min_salary):
                    min_salary = int(min_salary * cur["Valute"][currency]["Value"]) // 1000 * 1000
                if not np.isnan(max_salary):
                    max_salary = int(max_salary * cur["Valute"][currency]["Value"]) // 1000 * 1000
        return max_salary, min_salary

    @staticmethod
    def sj_salary(salary):
        salary = ",".join(salary)
        salary = salary.replace("\xa0", "").replace(" ", "")
        if not re.findall('[0-9]+', salary):
            min_salary = np.nan
            max_salary = np.nan
        elif re.findall('^от[0-9]+', salary):
            min_salary = int(re.findall('[0-9]+', salary)[0])
        elif re.findall('^до[0-9]+', salary):
            max_salary = int(re.findall('[0-9]+', salary)[0])
        elif len(re.findall('[0-9]+', salary)) == 1:
            min_salary = int(re.findall('[0-9]+', salary)[0])
            max_salary = int(re.findall('[0-9]+', salary)[0])

        else:
            min_salary = int(re.findall('[0-9]+', salary)[0])
            max_salary = int(re.findall('[0-9]+', salary)[1])

        if re.findall('[A-Z]', salary):
            currency = re.findall('[A-Z]{2,5}', salary)[0]
            if not np.isnan(min_salary):
                min_salary = int(min_salary * cur["Valute"][currency]["Value"]) // 1000 * 1000
            if not np.isnan(max_salary):
                max_salary = int(max_salary * cur["Valute"][currency]["Value"]) // 1000 * 1000
        return max_salary, min_salary

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['max_salary'], item['min_salary'] = self.hh_salary(item['salary'])
        elif spider.name == 'sjru':
            item['max_salary'], item['min_salary'] = self.sj_salary(item['salary'])
        del item['salary']

        collections = self.mongo_base[spider.name]
        collections.update_one({'url': item['url']}, {'$set': item}, upsert=True)

        return item
