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
    users_for_parse = ['anastasiya__kurkova','ndudchenko411']
    friendships_url = 'https://i.instagram.com/api/v1/friendships/'
    partitions = ['following', 'followers']

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
                for part in self.partitions:
                    yield response.follow(
                        f'/{user_for_parse}',
                        callback=self.following_user_parse,
                        cb_kwargs={'username': user_for_parse,
                                   'part': part
                                   }
                    )

    def following_user_parse(self, response: HtmlResponse, username, part):
        user_id = self.fetch_user_id(response.text, username)
        count = 12
        if part == 'following':
            url_friendships = f'{self.friendships_url}{user_id}/{part}/?count={count}'
        else:
            url_friendships = f'{self.friendships_url}{user_id}/{part}/?count={count}&search_surface=follow_list_page'
        yield response.follow(url_friendships,
                              callback=self.following_user_info_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'count': count,
                                         'part': part
                                         },
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def following_user_info_parse(self, response: HtmlResponse, username, user_id, count, part):
        j_data = response.json()
        if j_data.get('next_max_id'):
            max_id = int(j_data['next_max_id'])
            if part == 'following':
                next_url = f'{self.friendships_url}{user_id}/{part}/?count={count}&max_id={max_id}'
            else:
                next_url = f'{self.friendships_url}{user_id}/{part}/?count={count}&max_id={max_id}&search_surface=follow_list_page'
            yield response.follow(next_url,
                                  callback=self.following_user_info_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'count': count,
                                             'part': part
                                             },
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                  # ВАЖНО! БЕЗ ЗАГОЛОВКА НЕ БУДЕТ ОТКРЫВАТЬ!
                                  )
        following_users = j_data['users']
        for user in following_users:
            item = InstaparserItem(
                my_user_id=user_id,
                my_username=username,
                other_user_fullname=user['full_name'],
                other_user_photo=user['profile_pic_url'],
                other_user_id=user['pk'],
                other_username=user['username'],
                partition=part

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
