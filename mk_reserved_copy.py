import requests
import os
from pprint import pprint
import time
from tqdm import tqdm
from configparser import ConfigParser


# token_yd = 'AQAAAABi21uyAADLW7Io3Yx3HEvOk7JA7QV9OQg'


def get_photos(user_id, count):
    """"Возвращает список фотографий с именем, размером и ссылкой на файл. Является основой для других функций """
    url = 'https://api.vk.com/method/photos.get'
    parser = ConfigParser()
    parser.read('setting.ini')
    token = parser.get('database_config', 'token_vk')
    params = {'owner_id': user_id, 'access_token': token, 'v': '5.131', 'count': count, 'album_id': 'profile',
              'extended': '1'}
    response = requests.get(url, params=params)
    res = response.json()
    dic_res = {}
    l_output = []
    l_likes = []
    for item in res['response']['items']:  # Перебирает фотографии в цилке.
        if item['likes']['count'] in l_likes:  # Проверяет совпадает ли количество лайков у фотографий
            dic_res['filename'] = f"{item['likes']['count']}_{item['date']}.jpg "  # Если да, то добавляем дату в
            # название фото
        else:
            dic_res['filename'] = f"{item['likes']['count']}.jpg "
            l_likes.append(item['likes']['count'])
        dic_sizes = {}
        for foto in item['sizes']:  # Находит  соотношение ширины/высоты фотографий
            z = (foto['width'] / foto['height'])  # Здесь применина логика максимального соотношения
            # - ширина/высота(как в ТЗ...)
            dic_sizes[z] = foto['url']
        max_size = max(dic_sizes.keys())  # Находит максимальный размер для отправки на ЯД
        prop_foto = dic_sizes[max_size]
        dic_res['size'] = round(max_size, 3)
        dic_res['link'] = prop_foto
        l_output.append(dic_res)  # Формирует словарь с имеенем фотографии, размера, ссылки. Этот словарь -
        # база для других функций
    return l_output


def show_info(user_id, count):
    """"Возвращает информацию о сохраненных фотографиях в требуемом формате """
    l_output = []
    dic = {}
    for elem in get_photos(user_id, count):
        dic['filename'] = elem['filename']
        dic['size'] = elem['size']
        l_output.append(dic)
    return l_output


def get_links(user_id, count):
    """"Возвращает словарь с ссылками на фотографии, как значения, и названиями как ключами"""
    l_output = []
    dic = {}
    for elem in get_photos(user_id, count):
        dic[elem['filename']] = elem['link']
        l_output.append(dic)
    return l_output


def mk_yd_dir(token_yd):
    """"Создает специальную директорию на ЯД для хранения резервных фото"""
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    path = 'ReservedFoto'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token_yd)}
    response = requests.put(f'{url}?path={path}', headers=headers)
    if response.status_code == 201:
        print(f'dir {path} created!')


def get_upload_link(filename, token_yd):
    """"Возвращает  ссылку на загрузку на ЯД по имени файла"""
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token_yd)
    }
    params = {"path": f'ReservedFoto/{filename}', "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=params)
    if response.status_code == 200 or 201:
        pass


def uploader(filename, link, token_yd):
    """"Определяет механизм загрузки на ЯД"""
    get_upload_link(filename, token_yd)
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token_yd)
    }
    params = {"path": f'ReservedFoto/{filename}', "url": link, "overwrite": "true"}
    requests.post(upload_url, headers=headers, params=params)
    print(f'File {filename} uploaded to YandexDisk!')


def upload_to_disk(user_id, count, token_yd):
    """"Загружаеет непосредственно фотографии на ЯД"""
    l_links = get_links(user_id, count)
    for elem in tqdm(l_links):  # Перебирает ссылки на фотографии. Подключает прогресс-бар.
        for filename, link in elem.items():
            get_upload_link(filename, token_yd)
            uploader(filename, link, token_yd)
    time.sleep(0.5)


def id_screen_name(id_screenname):
    """"Возвращает id после пользовательского ввода id или screen_name """
    url = 'https://api.vk.com/method/users.get'
    parser = ConfigParser()
    parser.read('setting.ini')
    token = parser.get('database_config', 'token_vk')
    params = {'user_ids': id_screenname, 'fields': 'screen_name','access_token': token, 'v': '5.131'}
    response = requests.get(url, params=params)
    res = response.json()
    return res['response'][0]['id']


def mk_reserved_copy():
    """"Результирующая функция, принимает пользовательский вввод user_id ,count, token"""
    id_screenname = input("Введите целевой профиль ( id или screen_name):  ")
    token_yd = input("Введите  token_yd:  ")
    count = input("Введите  count - необходимое количество фотографий:  ")
    if not count.isdigit():  # В случае не корректного ввода количества фотографий,
        # устанавливается количество по умолчанию
        count = 5
    mk_yd_dir(token_yd)
    id_screen_name(id_screenname)
    upload_to_disk(id_screen_name(id_screenname), count, token_yd)
    show_info(id_screen_name(id_screenname), count)


if __name__ == "__main__":
    mk_reserved_copy()
