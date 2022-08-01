import requests
import datetime
import time

# Функции, задействованные в работе основного скрипта

# Функция отправления сообщения о новом комментарии в Телеграм
# Идентификатор чата, сообщество мониторинга, ид поста, ид комментария, текст комментария, дата комментария
def tg_message(chat_id, group, post_id, com_id, com_text, com_date, token):
    com_date = datetime.datetime.utcfromtimestamp(com_date + 10800).strftime('%Y-%m-%d %H:%M:%S')
    url = 'https://vk.com/wall{group}_{post_id}?w=wall{group}_{post_id}_r{com_id}'.format(group=group, post_id=post_id,
                                                                                          com_id=com_id)
    message = '🆘 Новый комментарий в сообществе!\n➡ Текст комментария:\n{}\n➡ Ссылка:\n{}\n➡ Дата публикации: {}'.format(
        com_text, url, com_date)
    tg = requests.get(f'https://api.telegram.org/bot{token}/sendMessage',
                      params={'chat_id': chat_id, 'text': message})

# Отправка тестового сообщения в телеграм
def tg_message_test(chat_id, token):
    try:
        message = 'Тестовая отправка в телеграм-чат!'
        tg = requests.get(f'https://api.telegram.org/bot{token}/sendMessage',
                          params={'chat_id': chat_id, 'text': message})
        print('Тестовое сообщение успешно отправлено! Проверьте чат')
    except Exception:
        print('Тестовое сообщение не отправлено. Проверьте настройки.')

# Парсинг комментариев в ВКонтакте
# Переменные f,f1, data не локализованы в данном модуле
def vk_parsing(MONITORING_GROUPS, TOKEN_VK, CHAT_ID_TG, TOKEN_TG):

    # Создаем файл (если не существует), где будет храниться информация о комментариях
    f = open('all_comments.txt', 'r+', encoding='utf-8')
    data = f.read().splitlines()

    # Создаем (если не существует) лог-файл
    f1 = open('comtotg.log', 'a', encoding='utf-8')

    # Определяем текущее время
    now = datetime.datetime.now()

    # Запись в лог
    f1.write('Скрипт запущен ' + now.strftime('%d-%m-%Y %H:%M') + '\n')

    # Запускаем сборщик комментариев
    try:
        for group in MONITORING_GROUPS:

            # Получаем последние 100 постов из сообщества для мониторинга
            group_posts = requests.get('https://api.vk.com/method/wall.get',
                                       params={'owner_id': group, 'access_token': TOKEN_VK, 'v': '5.81',
                                               'count': 100, 'offset': 0, 'filter': 'owner'})
            k = group_posts.json()

            # На случай если в сообществе мониторинга менее 100 публикаций
            if k['response']['count'] < 100:
                posts = k['response']['count']
            else:
                posts = 100

            post_number = 0

            # Пока номер спарсенного поста меньше 100 (или меньше кол-ва постов в сообществе, если их меньше 100)
            while post_number < posts:

                # Проверяем, есть ли комментарии у текущего поста
                if k['response']['items'][post_number]['comments']['count'] != 0:
                    print(k['response']['items'][post_number]['comments']['count'])

                    # Получаем id текущего поста
                    post_id = k['response']['items'][post_number]['id']

                    # Пауза для соблюдения ограничения работы с API ВК
                    time.sleep(0.9)

                    # Получаем все комментарии текущего поста
                    post_comments = requests.get('https://api.vk.com/method/wall.getComments',
                                                 params={'owner_id': group, 'post_id': post_id, 'access_token': TOKEN_VK,
                                                         'v': '5.81', 'count': 100, 'offset': 0, 'filter': 'owner'})

                    k1 = post_comments.json()
                    com = 0

                    # Переменная - количество комментариев в текущем посте
                    comments_from_post = k1['response']['count']

                    # Распарсим все комментарии из текущего поста
                    while com < comments_from_post:

                        # Формируем строку комментария
                        dict = k1['response']['items'][com]

                        # Удаляем ненужные вложения
                        if 'attachments' in dict.keys():
                            del dict['attachments']

                        # Добавляем в словарь еще один ключ, связанный с текущим сообществом мониторинга
                        dict['group'] = group

                        # Проверяем, есть ли комментарий в файле с ранее собранными комментариями
                        result = str(dict) in data

                        # Если комментария нет - отправляем уведомления в телеграм
                        if not result:## Было if result == False:
                            f.write(str(dict) + '\n')

                            # Получаем id комментария, текс комментария и дату публикации комментария
                            com_id = k1['response']['items'][com]['id']
                            com_text = k1['response']['items'][com]['text']
                            com_date = k1['response']['items'][com]['date']

                            # Отправляем в ТГ найденный комментарий
                            tg_message(CHAT_ID_TG, group, post_id, com_id, com_text, com_date, TOKEN_TG)

                            # Запись в лог информации о новом комментарии
                            f1.write('Новый комментарий ' + str(dict) + '\n')
                            com += 1
                        else:
                            # Запись в лог информации о том, что комментарий существует
                            f1.write('Комментарий присутствует в базе' + str(dict) + '\n')
                            com += 1

                # Если нет комментариев под публикацией - счетчик +1
                # Если все комментарии обработаны - счетчик +1
                post_number += 1

    except Exception as exc:

        # Записываем ошибку в лог-файл
        f1.write('Критическая ошибка : ' + now.strftime('%d-%m-%Y %H:%M') + str(exc))

    # Запись в лог
    f1.write('Скрипт завершен ' + now.strftime('%d-%m-%Y %H:%M') + '\n')

    # Закрываем файлы после выполнения скрипта
    f.close()
    f1.close()