from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
mongo_base = client['instagram']
collection = mongo_base["friendships"]

#Написать запрос к базе, который вернет список подписчиков только указанного пользователя
for i in collection.find({'my_username': 'yanana_design', 'partition': 'followers'}):
    pprint(i)

#Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
for i in collection.find({'my_username': 'yanana_design', 'partition': 'following'}):
    pprint(i)