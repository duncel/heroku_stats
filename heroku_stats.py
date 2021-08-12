import streamlit as st
import numpy as np
import pandas as pd
import time
from datetime import datetime
import vk_api
import requests
import json

#token = '84425f061df9e16ed8b7083863ad7853803e7e14204ca7e76947bb92d1cd311b2f1f03dd7a93a90782568'
# https://vk.com/technopark
#--------------------------------------------------------

#Вводим токен вк
token = st.text_input('Вставить токен')

#--------------------------------------------------------

#Вводим ссылку на сообщество
url = st.text_input('Вставить ссылку на сообщество')
# Преобразую ссылку и достаем название паблика
#public_name = url.rsplit('/', 1)[1]
our_group = url[15:]


#--------------------------------------------------------

# Авторизация
def user_session(token):
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    return vk
vk = user_session(token)

#--------------------------------------------------------

# Собираем данные сообщества
fields = 'id,name,members_count'

def get_group_data(our_group):
    group_data = vk.groups.getById(group_id=our_group, fields=fields)
    return group_data
group_data = get_group_data(our_group)    

#--------------------------------------------------------

# Название сообщества
group_name = get_group_data(our_group)

def get_group_name(group_name):
    for group in group_name:
        return group['name']
group_name = get_group_name(group_name)
st.text('Сообщество:')
st.write(group_name)

#--------------------------------------------------------

# Получаем числовое значение owner_id для его подстановки далее
group_id = get_group_data(our_group)

def get_group_id(group_id):
    for group in group_id:
        return group['id']

group_id = get_group_id(group_id)
st.text('Цифровой идентификатор сообщества')
st.write(group_id)

#--------------------------------------------------------

# Получаем количество постов в сообществе
count = 1
owner_id = -group_id
fields = 'id,name,members_count'

def get_wall_data(owner_id, count):
    wall_data = vk.wall.get(owner_id=owner_id, count=count, fields=fields)
    return wall_data['count']

post_count = get_wall_data(owner_id, count)
st.text('Количество публикаций:')
st.write(post_count)

#--------------------------------------------------------

# Собираем данные
#our_group = public_name 
owner_id = group_id
count_posts = post_count #получаем кол-во постов

offset = 0      
count = 100 #максимум 100 постов       
data_posts = [] #сюда добавляем массив данных из цикла по 100 постов

while offset < count_posts:
    r = requests.get('https://api.vk.com/method/wall.get',
        params={'domain': our_group,
                'filter': 'all',                                      
                'count': count,
                'offset': offset,
                'access_token': token,
                'v': 5.131
                        }).json()

    
    data_posts += r['response']['items'] #добавляем результат итерации цикла в массив
    offset += count #смещаемся на 100   
    time.sleep(0.33)


stats = [] #сюда будем добавлять нужные данные из data_post

for record in data_posts:   
    text = record['text'] #текст поста               
    date = datetime.fromtimestamp(record['date']).strftime('%Y.%m.%d') #год-месяц-день публикации
    hour = datetime.fromtimestamp(record['date']).strftime('%H:%M:%S') #час-минута-секунда публикации
    attachment = {'photo':0, 'audio':0, 'video':0 , 'link':0, 'poll':0} #вложения, если пусто то будет 0, если нет то значение
    if 'attachments' in record: 
        for attach in record['attachments']:
            if attach['type'] in attachment:
                attachment[attach['type']] = attachment[attach['type']] + 1       
    # эти просмотры выебали голову    
    if 'views' in record: #до 2017 не было такой фичи как просмотры 
        views = record['views']['count'] #если есть то запизываем
    else:
        views = 0 #если пост старый и в массиве нет просмотров добавляем 0

    # добавляем данные в массив         
    stats.append([date, hour, record['comments']['count'], record['likes']['count'], record['reposts']['count'], views, text, attachment['photo'], attachment['audio'], attachment['video'], attachment['link'], attachment['poll']])


#--------------------------------------------------------

# Создаем список из слов которыми будут называться колонки
columns = ['date', 'hour', 'views', 'comments', 'likes', 'reposts', 'text', 'photo', 'audio', 'video', 'link', 'poll']

#--------------------------------------------------------

# создаем датафрейм с колонками и заполняем данными из stats
df = pd.DataFrame(data=stats, columns=columns) 

#--------------------------------------------------------

st.dataframe(df)

#--------------------------------------------------------

#Название приложения
#st.title(post_count)