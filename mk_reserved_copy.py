import requests
import os
from pprint import pprint
import time
from tqdm import tqdm


def get_photos(user_id, count):
    url = 'https://api.vk.com/method/photos.get'
    TOKEN = 'vk1.a.Mzw6RcIoNu_9PzREpj6DhhwDaYwlAei2CutnqE2sh3AbbEElUg2nJ9XUE-TwzLo4lJoIfp82DbEGj2idwyfhEEpUBXsk2BPmVuf8fklMZqjgdpIT-_8mDTu7WFpVlFZWjbdVZghSZpbM6-EoV4yBHX0JXK7RKsfYkeabSXLlXYaEmCkFez0dSgpEoQYAmH02'
    params = {'owner_id': user_id, 'access_token': TOKEN, 'v': '5.131', 'count': count, 'album_id': 'profile', 'extended': '1'}
    response = requests.get(url, params=params)
    res = response.json()
    dic_res = {}
    L_output = []
    L_likes = []
    for item in tqdm(res['response']['items']): #Проходим в цикле по фото, включаем прогресс-бар
        if item['likes']['count'] in L_likes:   #Проверяем совпадает ли количество лайков у фотографий
            dic_res['filename'] = f"{item['likes']['count']}_{item['date']}.jpg "#Если да, то добавляем дату в название фото
        else:
            dic_res['filename'] = f"{item['likes']['count']}.jpg "
        L_likes.append(item['likes']['count'])
        dic_sizes = {}
        for foto in item['sizes']:#Находим требуемое соотношение ширины/высоты фотографиии
            z = (foto['width'] / foto['height'])  # Здесь применина логика максимального соотношения - ширина/высота(как в ТЗ...)
            # Возможно требуется - max(foto['width'],foto['height']) or max((foto['width'])+(foto['height']))
            dic_sizes[z] = foto['url']
        max_size = max(dic_sizes.keys())#Находим максимальный размер, чтобы отправить эту фотографию на ЯД
        prop_foto = dic_sizes[max_size]
        filename = f"FOTOS/{dic_res['filename']}"
        respons = requests.get(prop_foto)#Запрос на получение адреса фотографии
        if respons.status_code == 200:
            print(f'{dic_res["filename"]} saved in local')
            with open(filename, 'wb') as imgfile:#Сохраняем на диске в проекте
                imgfile.write(respons.content)
        d_temp = {'size': round(max_size,3)}
        dic_res.update(d_temp)
        L_output+=dic_res.items()
        time.sleep(1)
    pprint(f"Список файлов - {L_output}")#Вывод списка файлов по требуемой форме


def mk_yd_dir():#Создание специальной директории на ЯД для хранения резервных фото
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    path = 'ReservedFoto'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token_yd)}
    response = requests.put(f'{url}?path={path}', headers=headers)
    if response.status_code == 201:
        print(f'dir {path} created!')


def _get_upload_link(filename):#Функция получает ссылку на загрузку на ЯД
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token_yd)
    }
    params = {"path": f'ReservedFoto/{filename}', "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=params)
    if response.status_code == 200 or 201:
        print(f"link for {filename} created")
    return response.json()


def upload_file_to_disk():#Функция загружает фото с локального диска на ЯД по полученной ссылке
    for filename in tqdm(os.listdir("FOTOS")):
        with open(os.path.join("FOTOS", filename), 'rb') as f:
            data = f.read()
            href = _get_upload_link(filename).get("href", "")
            response = requests.put(href, data=data)
            response.raise_for_status()
            if response.status_code == 201:
                 print(f"file {filename} uploaded!")
        time.sleep(1)
    print("Finished!")


token_yd = 'AQAAAAA87JNYAADLWz9Biym-aU5PoArcTu9Lt2g'
user_id = 123456


def mk_reserved_copy(user_id,count, token=token_yd):#Результурующая функция для сохраниния резервных копий и вывода
                                                    #информационного файла
    get_photos(user_id, count)
    mk_yd_dir()
    upload_file_to_disk()


mk_reserved_copy(user_id=user_id,token = token_yd,count=4)
