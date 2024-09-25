# import os
# from dotenv import load_dotenv
# import telebot
# from telebot import types

# # Загружаем переменные окружения из .env файла
# load_dotenv()

# # Получаем токен бота и список разрешённых пользователей
# BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
# ALLOWED_USER_IDS = list(map(int, os.getenv('ALLOWED_USER_ID', '').split(',')))

# # Инициализируем бота с токеном
# bot = telebot.TeleBot(BOT_API_TOKEN)

# # Команда /start


# @bot.message_handler(commands=['start'])
# def start(message):
#     if message.from_user.id in ALLOWED_USER_IDS:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         btnoff = types.KeyboardButton('⛔️ Выключить компьютер')
#         markup.add(btnoff)
#         bot.send_message(
#             message.chat.id, "Привет! Чем могу помочь?", reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, "У вас нет доступа к этой функции.")


# # Обработчик кнопки "Выключить компьютер"
# @bot.message_handler(content_types=['text'])
# def handle_text(message):
#     if message.from_user.id in ALLOWED_USER_IDS:
#         if message.text == '⛔️ Выключить компьютер':
#             bot.reply_to(message, "Выключаю компьютер...")

#             if os.name == 'nt':  # Windows
#                 os.system('shutdown /s /f /t 0')
#             elif os.name == 'posix':  # Linux/MacOS
#                 os.system('sudo shutdown now')
#         else:
#             bot.send_message(message.chat.id, "Неправильная команда.")
#     else:
#         bot.send_message(message.chat.id, "У вас нет доступа к этой функции.")


# # Запуск бота
# if __name__ == '__main__':
#     bot.polling(none_stop=True)

import os
from dotenv import load_dotenv
import telebot
from telebot import types
import paramiko
from loguru import logger

# Загружаем переменные окружения из .env файла
load_dotenv()


# Настраиваем Loguru
logger.add("bot_log.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")  # noqa # isort: ignore

# Получаем токен бота и список разрешённых пользователей
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS')
if ALLOWED_USER_IDS is None:
    raise ValueError("ALLOWED_USER_IDS не установлены в .env файле.")
ALLOWED_USER_IDS = list(map(int, ALLOWED_USER_IDS.split(',')))

# Получение путей к ключам из переменных окружения
private_key_linux1 = os.getenv('PRIVATE_KEY_PATH_LINUX1')
private_key_linux2 = os.getenv('PRIVATE_KEY_PATH_LINUX2')
private_key_windows = os.getenv('PRIVATE_KEY_PATH_WINDOWS')

# Проверка наличия ключей
if private_key_linux1 is None:
    raise ValueError("PRIVATE_KEY_PATH_LINUX1 не установлены в .env файле.")
if private_key_linux2 is None:
    raise ValueError("PRIVATE_KEY_PATH_LINUX2 не установлены в .env файле.")
if private_key_windows is None:
    raise ValueError("PRIVATE_KEY_PATH_WINDOWS не установлены в .env файле.")

# Инициализируем бота с токеном
bot = telebot.TeleBot(BOT_API_TOKEN)


# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in ALLOWED_USER_IDS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btnoff = types.KeyboardButton('⛔️ Выключить удаленные компьютеры')
        markup.add(btnoff)
        bot.send_message(
            message.chat.id, "Привет! Чем могу помочь?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой функции.")


# Функция для управления удалёнными компьютерами
def manage_remote_computers():
    # Список Linux машин и соответствующие пути к ключам
    linux_machines = [
        {"ip": "192.168.88.126", "port": 9091, "user": "root", "key_path": private_key_linux1},  # noqa # isort: ignore
        {"ip": "192.168.88.127", "port": 9091, "user": "root", "key_path": private_key_linux2}  # noqa # isort: ignore
    ]

    # Работа с Linux машинами
    for machine in linux_machines:
        ip = machine['ip']
        port = machine['port']
        user = machine['user']
        key_path = machine['key_path']

        logger.info(f"Попытка подключения к {ip}:{port}")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.info(f"Используем ключ {key_path} для подключения.")

            # Подключение
            ssh.connect(ip, port=port, username=user, key_filename=key_path)  # noqa # isort: ignore
            logger.info(f"Успешно подключились к {ip}. Отправляем команду на выключение.")  # noqa # isort: ignore
            # Выключение Linux машины
            stdin, stdout, stderr = ssh.exec_command('shutdown now')  # noqa # isort: ignore
            # Получение статуса выполнения команды
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                logger.info(f"Команда на выключение Линукс машины с ip {ip} выполнена успешно.")  # noqa # isort: ignore
            else:
                logger.error(
                    f"Команда завершилась с ошибкой. Код: {exit_status}")

            ssh.close()
        except Exception as e:
            logger.error(f"Ошибка при подключении к {ip}: {e}")

    # Список Windows машин и соответствующие пути к ключам
    windows_machines = [
        {"ip": "192.168.88.200", "port": 9092, "user": "Administrator", "key_path": private_key_windows}  # noqa # isort: ignore
    ]

    # Работа с Windows машинами
    for machine in windows_machines:
        ip = machine['ip']
        port = machine['port']
        user = machine['user']
        key_path = machine['key_path']

        logger.info(f"Попытка подключения к {ip}:{port}")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.info(f"Используем ключ {key_path} для подключения.")

            # Подключение
            ssh.connect(ip, port=port, username=user, key_filename=key_path)  # noqa # isort: ignore
            logger.info(f"Успешно подключились к {ip}. Отправляем команду на перезагрузку.")  # noqa # isort: ignore

            # Перезагрузка Windows машины
            stdin, stdout, stderr = ssh.exec_command('shutdown /r /t 0')  # noqa # isort: ignore

            # Получение статуса выполнения команды
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                logger.info(f"Команда на перезагрузку Windows машины с ip {ip} выполнена успешно.")  # noqa # isort: ignore
            else:
                logger.error(
                    f"Команда завершилась с ошибкой. Код: {exit_status}")

            ssh.close()
        except Exception as e:
            logger.error(f"Ошибка при подключении к {ip}: {e}")


# Обработчик кнопки "Выключить удаленные компьютеры"
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id in ALLOWED_USER_IDS:
        if message.text == '⛔️ Выключить удаленные компьютеры':
            bot.send_message(
                message.chat.id, "Выполняю команды для удаленных компьютеров...")
            manage_remote_computers()
            bot.send_message(message.chat.id, "Команды выполнены.")
        else:
            bot.send_message(message.chat.id, "Неправильная команда.")
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой функции.")


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)

''' После запускать бота командой 
sudo docker run -d --restart always \
    -v /home/mikh/magna-prv2:/home/mikh/magna-prv2 \
    -v /path/to/another/key:/path/to/another/key \
    -v /path/to/yet/another/key:/path/to/yet/another/key \
    имя_образа 
'''
