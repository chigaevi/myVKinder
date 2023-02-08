import requests
import os
from modules.vkinder_db import find_user, user_exists_in_blocklist
from heapq import nlargest


# предварительно прописываем в Environment Variables переменную с именем gr_token с ключем от сообщества
group_token = os.getenv('gr_token')
# предварительно прописываем в Environment Variables переменную с именем ad_token с ключем от пользователя
admin_token = os.getenv('ad_token')

url = 'https://api.vk.com/method/'


class vkinder:
    def __init__(self, user_id): # передаем id пользователя
        self.user_id = user_id

    # метод получения информации по пользователю для дальнейшего поиска по ним
    def get_user_info(self):
        method = 'users.get'
        params = {
            'user_ids': self.user_id,
            'access_token': group_token,
            'v': '5.131',
            'fields': 'bdate, sex, city, is_closed',
        }
        res = requests.get(url + method, params=params)
        info_for_search = {}
        info_for_search['city'] = res.json()['response'][0]['city']['id']
        info_for_search['sex'] = res.json()['response'][0]['sex']
        try:
            b_year = res.json()['response'][0]['bdate']
            if len(b_year) == 10:
                info_for_search['b_year'] = b_year[-4:]
            else:
                info_for_search['b_year'] = None
        except KeyError:
            info_for_search['b_year'] = None

        return info_for_search

    # метод формирует список для attachment метода messages.send в виде <type><owner_id>_<media_id> (https://dev.vk.com/method/messages.send)
    def get_photo_user(self, owner_id, num=3):  # num определяет количество максимально залайканых фото
        method = 'photos.get'
        params = {
            'owner_id': owner_id,
            'access_token': admin_token,
            'v': '5.131',
            'album_id': 'profile', # wall — фотографии со стены, profile — фотографии профиля, saved — сохраненные фотографии. Возвращается только с ключом доступа пользователя.
            'extended': '1' # будут возвращены дополнительные поля likes, comments, tags, can_comment, reposts. По умолчанию: 0.
        }
        res = requests.get(url + method, params=params)
        item_list = res.json()['response']['items']

        # собираем список лайков:
        count_likes_list = []
        for item in item_list:
            count_likes_list.append(item['likes']['count'])
        # находим num максимальных лайков с помощью модуля heapq
        max_count_likes_list = nlargest(num, count_likes_list)
        # формируем список максимально залайканых
        max_likes_photo_list = []
        for max_count_likes in max_count_likes_list:
            for item in item_list:
                if len(max_likes_photo_list) == num: #проверка нужна что бы избежать ситуации когда у человека несколько фото с одинаковым числом лайков
                    continue
                if item['likes']['count'] == max_count_likes:
                    max_likes_photo_list.append('photo' + str(item['owner_id']) + '_' + str(item['id']))
        return max_likes_photo_list

    # проверка приватности страницы пользователя по id в VK
    def privacy_check(self, owner_id):
        method = 'users.get'
        params = {
            'user_ids': owner_id,
            'access_token': group_token,
            'v': '5.131',
            'fields': 'is_closed',
        }
        owner_res = requests.get(url + method, params=params)
        if owner_res.json()['response'][0]['is_closed']:  # проверка приватности страницы
            return True
        else:
            return False


    # метод формирует список
    def search_users_info(self, search_caunt=15):  # search_caunt - число пользователей в выдаче
        user_info = self.get_user_info()
        user_city = user_info['city']
        user_sex = user_info['sex']
        user_b_year = user_info['b_year']
        if user_sex == 1:
            sex = 2
        else:
            sex = 1
        method = 'users.search'
        params = {
            'access_token': admin_token,
            'v': '5.131',
            'sex': sex,
            'city': user_city,
            'count': search_caunt,
            'has_photo': 1,
            'verified': 1,
            'is_closed': True,
            'birth_year': user_b_year,
            'fields': 'bdate, sex, city',
        }
        res = requests.get(url + method, params=params)

        # создаем словарь с именем фамилией, ссылкой на профиль найденых людей и списком из get_photo_user(owner_id)
        result_list = []
        # db_user_id = find_user(vk_id_user=self.user_id)[0]
        for item in res.json()['response']['items']:
            # if not user_exists_in_blocklist(db_user_id, str(item['id'])):
                result_list.append([
                    item['first_name'] + ' ' + item['last_name'],
                    'https://vk.com/id' + str(item['id']), str(item['id'])
                ])

        return result_list
