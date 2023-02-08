import vk_api
import os
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from modules.keyboards import keyboard_start, keyboard_second, keyboard_main
from modules.vkinder_class import vkinder
from modules.vkinder_db import add_user, find_user, add_favorite, veiw_favorites, user_exist, favorite_exist, \
    add_user_in_blocklist, user_exists_in_blocklist

# предварительно прописываем в Environment Variables переменную с именем gr_token с ключем от сообщества
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


def show_candidate(item, user_vk, user_id):
    """Функция проверяет профиль кандидата и выдает его данные: имя, фамилию, ссылку на профиль и 3 фото с наибольшим
    числом лайков или выводит сообщение, если профиль закрыт"""
    if user_vk.privacy_check(item[2]):  # проверяем закрытость профиля
        # send_message(user_id, f'Кандидат № {i}')
        send_message(user_id, item[0], keyboard_main.get_keyboard())  # выдаем имя
        send_message(user_id, item[1], parse_links=1)  # выдаем ссылку
        send_message(user_id, 'Это закрытый профиль. Фото не доступны :(')
        send_message(user_id, 'идём дальше ?')
        photo_list = [None, None, None]  # значения которые запишутся в БД при добавлении в избранное
    else:
        # send_message(user_id, f'Кандидат № {i}')
        send_message(user_id, item[0], keyboard_main.get_keyboard())  # выдаем имя
        send_message(user_id, item[1], parse_links=1)  # выдаем ссылку
        # получаем список фото в формате для attachment:
        photo_list = user_vk.get_photo_user(owner_id=item[2])
        # выдаем фото в цикле так как не у всех людей на странице есть три фото:
        for attachment in photo_list:
            send_message(user_id, '--------------------------', attachment=attachment)
    return photo_list


def start_vk_bot():
    print('VKinder bot started')
    i = 0  # индекс кандидата в списке
    fwrd = 1  # проверека направления движения по списку: 1 - вперед, 0 - назад
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            # Получаем id юзера и текст сообщения:
            user_id = str(event.user_id)
            text = event.text.lower()
            # создаем объект класса vkinder:
            user_vk = vkinder(user_id)
            # Проверяем на наличие такого юзера в БД, если нет создаем
            if not user_exist(vk_id_user=user_id):
                add_user(user_id)
            # вытаскиваем id юзера из БД (реализация find_user корявая надо переделать)
            db_user_id = find_user(vk_id_user=user_id)[0]
            if text == 'начать':
                send_message(user_id, 'Хочешь найти своё счастье?', keyboard_start.get_keyboard())
            elif text == 'привет':
                send_message(user_id, 'Привет!', keyboard_start.get_keyboard())
            elif text == 'искать':
                send_message(user_id, 'Тогда начинаем.')
                # создаем лист с результатами поиска (search_caunt - число пользователей в выдаче, максимально 1000):
                result_list = user_vk.search_users_info(search_caunt=1000)
                count = len(result_list)
                send_message(user_id, f'Для Тебя найдено {count} варианта(ов). Нажимай "просмотр" ',
                             keyboard_second.get_keyboard())

            elif text == 'вперед' or text == 'просмотр':
                if fwrd == 0:
                    i += 1
                if i > count - 1:
                    send_message(user_id, 'Вы просмотрели всех кандидатов, начинаем сначала')
                    i = 0
                item = result_list[i]
                i += 1
                fwrd = 1
                photo_list = show_candidate(item, user_vk, user_id)

            elif text == 'назад':
                if fwrd == 1:
                    i -= 2
                else:
                    i -= 1
                if i < 0:
                    send_message(user_id, 'Вы находитесь в начале списка кандидатов')
                    i = 0
                    continue
                item = result_list[i]
                fwrd = 0
                photo_list = show_candidate(item, user_vk, user_id)

            elif text == 'в избранное':
                if favorite_exist(item[0]):
                    send_message(user_id, 'Такая запись уже есть')
                else:
                    add_list = [db_user_id, item[0], item[1], photo_list]
                    add_favorite(add_list)
                    send_message(user_id, 'Добавил!')

            elif text == 'посмотреть избранное':
                favorites_list = veiw_favorites(db_user_id)
                if len(favorites_list) != 0:  # проверяем есть ли что-то в избранном
                    for favorite_item in favorites_list:
                        send_message(user_id, favorite_item[0])
                        send_message(user_id, favorite_item[1], parse_links=1)
                else:
                    send_message(user_id, 'в избранном ничего нет')

            elif text == 'в чёрный список':

                if user_exists_in_blocklist(db_user_id, item[2]):
                    send_message(user_id, 'Такая запись уже есть')
                else:
                    add_user_in_blocklist(db_user_id, item[2])
                    send_message(user_id, 'Добавил!')

            else:
                send_message(user_id, 'Не понял Вас. Что нужно сделать?', keyboard_start.get_keyboard())
