import json
import module

# Загружаем настройки из конфигурационного файла
with open('config.json') as f2:
    config_const = json.load(f2)

TOKEN_VK = config_const['TOKEN_VK']
TOKEN_TG = config_const['TOKEN_TG']
MONITORING_GROUPS = list(config_const['MONITORING_GROUPS'])
CHAT_ID_TG = config_const['CHAT_ID_TG']
f2.close()

def main():

    # Основная функция
    # Аргументы: список групп для мониторинга, токен ВК, чат для отправки в ТГ, токен ТГ
    module.vk_parsing(MONITORING_GROUPS, TOKEN_VK, CHAT_ID_TG, TOKEN_TG)

# Запуск основной функции
main()
