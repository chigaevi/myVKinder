import vk_api
import os
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from modules.keyboards import keyboard_start, keyboard_main
from modules.vkinder_class import vkinder
from modules.vkinder_db import add_user, find_user, add_favorite, veiw_favorites, user_exist, favorite_exist

group_token = os.getenv('gr_token')
session = vk_api.VkApi(token=group_token)

def send_message(user_id, message, keyboard=None, parse_links=None, attachment=None):
    post = {
        'user_id': user_id,
        'message': message,
        'random_id': random.randrange(10 ** 10)
    }
    if keyboard is not None:
        post['keyboard'] = keyboard
    if parse_links is not None:
        post['dont_parse_links'] = 0
    if attachment is not None:
        post['attachment'] = attachment
    session.method('messages.send', post)


def start_VK_bot():
    print('VKinder bot started')
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            # Получаем id юзера и текст сообщения:
            user_id = str(event.user_id)
            text = event.text.lower()
            # создаем объект класса vkinder:
            user_vk = vkinder(user_id)
            # Проверяем на наличие такого юзера в БД, если нет создаем (реализация find_user корявая надо переделать)
            if not user_exist(vk_id_user=user_id):
                add_user(user_id)
            # вытаскиваем id юзера из БД (реализация find_user корявая надо переделать)
            db_user_id = find_user(vk_id_user=user_id)[0]

            if text == 'начать':
                send_message(user_id, 'Хочешь найти своё счастье?', keyboard_start.get_keyboard())
            elif text == 'привет':
                send_message(user_id, 'Привет!', keyboard_start.get_keyboard())
            elif text == 'искать':
                send_message(user_id, 'Тогда начинаем. Немного нужно подождать...')
                # создаем лист с результатами поиска (search_caunt - число пользователей в выдаче):
                result_list = user_vk.search_users_info(search_caunt=35)
                # длинна получившегося списка будет меньше search_caunt так как будут пропускаться закрытые профили
                count = len(result_list)
                send_message(user_id, f'Для Тебя найдено {count} варианта(ов). Нажимай "дальше" ',
                             keyboard_main.get_keyboard())
                # создаем итерируемый список чтобы можно было использовать метод next() при показе:
                iter_result_list = iter(result_list)
                i = 1
            elif text == 'дальше' and i <= count: #здесь лучше реализовать всё через выборку из бд и двигаться for по id
                i += 1
                item = next(iter_result_list) #двигаемся по листу
                send_message(user_id, item[0]) #выдаем имя
                send_message(user_id, item[1], parse_links=1) #выдаем ссылку
                # выдаем фото в цикле так как не у всех людей на странице есть три фото
                for attachment in item[2]:
                    send_message(user_id, '--------------------------', attachment=attachment)
                if i > count:
                    send_message(user_id, 'больше вариантов нет')

            elif text == 'в избранное':
                if favorite_exist(item[0]):
                    send_message(user_id, 'Такая запись уже есть')
                else:
                    add_list = [db_user_id, item[0], item[1], item[2]]
                    add_favorite(add_list)
                    send_message(user_id, 'Добавил!')

            elif text == 'посмотреть избранное':
                favorites_list = veiw_favorites(db_user_id)
                if len(favorites_list) != 0: # проверяем есть ли что-то в избранном
                    for favorite_item in favorites_list:
                        send_message(user_id, favorite_item[0])
                        send_message(user_id, favorite_item[1], parse_links=1)
                else: send_message(user_id, 'в избранном ничего нет')

            else:
                send_message(user_id, 'Не понял Вас. Что нужно сделать?', keyboard_start.get_keyboard())