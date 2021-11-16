import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = '13.nicole.48'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1637092992:Ab1QAC3x04iyvOs+YBp9bNOxX+4NAsERi0D2X46SuZIaL/djThwdjc1XonmES6J23YZtltCVWL5xiECL0Uyhyyk+XeI1X46ZXnHuOY32WbXsfmklZ6kA9gwyy8V+SCWS+R2NEddsRK9JPbWSO7RB'
    users_for_parse = ['fideliskihongole']
    friendships_url = 'https://i.instagram.com/api/v1/friendships/'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user_for_parse in self.users_for_parse:
                yield response.follow(
                    f'/{user_for_parse}',
                    callback=self.following_user_parse,
                    cb_kwargs={'username': user_for_parse}
                )

    def following_user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        count = 12
        url_friendships = f'{self.friendships_url}{user_id}/following/?count={count}'
        yield response.follow(url_friendships,
                              callback=self.following_user_info_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'count' : count
                                         },
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def following_user_info_parse(self, response:HtmlResponse, username, user_id, count):
        j_data = response.json()
        if j_data['next_max_id']:
            max_id = int(j_data['next_max_id'])
            url_friendships = f'{self.friendships_url}{user_id}/following/?count={count}&max_id={max_id}'
            yield response.follow(url_friendships,
                                  callback=self.following_user_info_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'count': count}
                                  )
        following_users = j_data['users']
        for user in following_users:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                fullname=user['full_name'],
                photo=user['profile_pic_url'],

            )
            yield item


    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')