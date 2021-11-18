import scrapy
from scrapy.http import HtmlResponse
import re
import json
from instaparser.items import InstaparserItem


class InstagramFollowersSpider(scrapy.Spider):
    name = 'instagram_followers'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'ivankurkov4'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1637240427:AchQAJb/6IF+KcsS5zy9ldJwooK7RSvY7wRRc2b5k3knHtBsBk1Cdg+kMU/52oy40J/ykno0euQqQgQscvTbQXCyHhtwXU0xWyHnP4Jot54zW0am5tC9L6TKiiMznzaPNxlOLx4OXVmT9Wo='
    users_for_parse = ['anastasiya__kurkova', 'yanana_design', 'eremin.aleksandr1008']
    friendships_url = 'https://i.instagram.com/api/v1/friendships/'
    partitions = 'followers'

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
                    callback=self.followers_user_parse,
                    cb_kwargs={'username': user_for_parse,
                               'part': self.partitions
                               }
                )

    def followers_user_parse(self, response: HtmlResponse, username, part):
        user_id = self.fetch_user_id(response.text, username)
        count = 25
        url_friendships = f'{self.friendships_url}{user_id}/{part}/?count={count}&search_surface=follow_list_page'
        yield response.follow(url_friendships,
                              callback=self.followers_user_info_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'count': count,
                                         'part': part
                                         },
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def followers_user_info_parse(self, response: HtmlResponse, username, user_id, count, part):
        j_data = response.json()
        if j_data.get('next_max_id'):
            max_id = int(j_data['next_max_id'])
            next_url = f'{self.friendships_url}{user_id}/{part}/?count={count}&max_id={max_id}&search_surface=follow_list_page'
            yield response.follow(next_url,
                                  callback=self.followers_user_info_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'count': count,
                                             'part': part
                                             },
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                  # ВАЖНО! БЕЗ ЗАГОЛОВКА НЕ БУДЕТ ОТКРЫВАТЬ!
                                  )
        followers_users = j_data['users']
        for user in followers_users:
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
