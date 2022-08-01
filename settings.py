import requests
import json

# Скрипт создан исключительно для получения и обработки настроек
# Вы можете загрузить все настройки в файл config.json без запуска данного скрипта

# Из того, что нужно добавить:
# Получение идентификатора чата телеграма через getUpdates
# Валидация токена телеграм
# Недопуск записи пустых значений в конфигурационный файл (перезапуск ввода до получания валидного значения)


# Формирует настройки для работы скрипта через введенные значения командной строки
def create_config():

    config_const = dict.fromkeys(['TOKEN_VK', 'TOKEN_TG','MONITORING_GROUPS','CHAT_ID_TG'])

    # Запись токена ВКонтакте
    print("Введите значение Токена ВКонтакте")
    input_var = input()

    # Проверяем введенный токен на валидность
    if check_token_VK(input_var) == True:
        # Если токен валидный - записываем в файл
        config_const['TOKEN_VK'] = input_var
    else:
        pass

    # Запись токена Телеграм
    print("Введите значение Токена Телеграм, полученный у BotFather")
    config_const['TOKEN_TG'] = input()
    print("Введите идентификаторы сообществ для мониторинга (сообщетсва ВК). \n"
          "Ввод по одному сообществу. Для завершения и перехода к следующему шагу нажмите '1'. ")

    # Запись списка с идентификаторами сообществ для мониторинга
    config_const['MONITORING_GROUPS'] = []

    while True:
        input_var = input()

        # Убрали проверку на число, чтобы исключить ошибку, если на входе строка
        if input_var != '1':

            # Если идентификатор начинается с минуса и не содержит ничего кроме цифр(кроме первого символа)
            if input_var.startswith('-') and input_var[1:len(input_var)].isdigit():
                config_const['MONITORING_GROUPS'].append(input_var)
                print('Идентификатор записан. Введите следующий идентификатор. Для следующего шага нажмите 1')
            else:
                print("Ошибка!\nИдентификатор сообщества должен начинаться с символа '-' и не должен содержать букв! Идентификатор некорректен.")
        else:
            print('Список сообществ сформирован')
            break

    # Запись идентификатора чата в Телеграме, куда будут отправляться сообщения
    print("Введите ид чата для отправки сообщений")
    config_const['CHAT_ID_TG'] = input()

    # Запись настроек в конфигурационный файл
    with open('config.json', 'w') as f:
        f.write(json.dumps(config_const))
    f.close()

    print("Настройки записаны!")
    print(config_const)


# Проверяет токен ВК на валидность
def check_token_VK(token_VK):

    # Для проверки токена на валидность отправляем запрос на получение информации о странице Павла Дурова
    r = requests.get('https://api.vk.com/method/users.get', params={'access_token': token_VK, 'v': '5.81', 'user_ids': 1})
    k = r.json()

    try:
        if k['response'][0]['last_name'] == 'Дуров':
            print('Токен ВКонтакте валидный')
            return True
        else:
            pass

    except Exception:
        print('Токен ВКонтакте невалидный или Павел Дуров сменил фамилию :(')
        return False


# Определяем идентификатор чата в телеграме на основе getUpdates
# Не доработана, необходимо создавать группу, а не канал
def get_chat_id_tg(token):

    tg = requests.get(f'https://api.telegram.org/bot{token}/getUpdates')
    k = tg.json()

    # Телеграм возвращает пустой ответ, если бот работает(запущен)
    if k['result'] == []:
        print("Бот включен и уже обработал все сообщения. Временно выключите его и повторите попытку.")
    else:
        print(k)
        #print(k['result'][0]['my_chat_member']['chat'])
        #print(k['result'][0]['my_chat_member']['chat']['id'])


# Функция, определяюшая источник настроек - из командной строки или из конфигурационного файла
def get_settings():

    print("Привет! Это первый запуск скрипта. \n"
          "Вы можете загрузить настройки через файл config.json (Введите '1') или через командную строку (Введите '2')")

    settings_download = input()

    # Пока пользователь не введет 1 или 2
    while settings_download != 1 or 2:

        # Если на вход пришло целое число в диапазоне от 1 до 2
        if settings_download.isdigit() and 1 <= int(settings_download) <= 2:

            if int(settings_download) == 1:
                print("Настройки будут загружены из файла config.json")

                try:
                    # Читаем конфигурационный файл
                    with open('config.json') as f:
                        config_const = json.load(f)

                    # Выводим значения настроек
                    print("Загружен Токен ВКонтакте: " + config_const['TOKEN_VK'])
                    print("Загружен Токен Телеграм: " + config_const['TOKEN_TG'])
                    print(f"Загружены группы мониторинга: {config_const['MONITORING_GROUPS']}")
                    print(f"Загружен ид чата для отправки сообщений: {config_const['CHAT_ID_TG']}")
                    break

                except Exception:
                    print("Конфигурационный файл не существует. Сформируйте его или воспользуйтесь ручным вводом. Перезапустите скрипт после устранения проблемы.")
                    exit()

            elif int(settings_download) == 2:
                create_config()
                break
            else:
                pass
        # Если на вход пришло что-то отличное от 1 и 2, выводим поле ввода заново
        else:
            print("Такого варианта загрузить настройки пока нет( \nВведите '1' или '2'")
            settings_download = input()

    print('Настройки успешно сохранены. Скрипт готов к работе. Запустите на сервере основной файл скрипта.')

def main():
    get_settings()
main()
