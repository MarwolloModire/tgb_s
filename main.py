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

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота и список разрешённых пользователей
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS')
if ALLOWED_USER_IDS is None:
    raise ValueError("ALLOWED_USER_IDS не установлены в .env файле.")
ALLOWED_USER_IDS = list(map(int, ALLOWED_USER_IDS.split(',')))

# Получаем путь к приватному ключу из переменной окружения
private_key_path = os.getenv('PRIVATE_KEY_PATH')
if private_key_path is None:
    raise ValueError("PRIVATE_KEY_PATH не установлены в .env файле.")

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
    # Выключение Linux машин
    linux_ips = ['192.168.88.126']
    linux_port = 9091
    linux_user = 'magna'  # Имя пользователя

    for ip in linux_ips:
        try:
            # Используем Paramiko для SSH подключения и выполнения команды
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=linux_port, username=linux_user,
                        key_filename=private_key_path)  # Используем путь к ключу
            ssh.exec_command('sudo shutdown now')  # Выключение Linux
            ssh.close()
        except Exception as e:
            print(f"Ошибка при подключении к {ip}: {e}")


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
