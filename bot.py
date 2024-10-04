import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import json

# Задайте токен вашего бота
bot_token = '7229675025:AAFuDM5dbfuhYv_8o3NPmnvgZnibiHD8Zrc'
bot = telebot.TeleBot(bot_token)

#GLOBAL VAR
user_data = {}
current_directory = os.path.dirname(__file__)
dir_files = os.path.join(current_directory, 'files')
dir_images = os.path.join(current_directory, 'images')

global name_file_allocation_12
global name_file_allocation_15
global name_file_promo
global name_file_sc
global name_file_honor_logo
global name_file_user_ids

#Название файлов
name_file_allocation_12 = 'Allocation12.xlsx'
name_file_allocation_15 = 'Allocation15.xlsx'
name_file_sc = 'HONOR_service.xlsx'
name_file_promo12 = 'Promoplan12%.xlsx'
name_file_promo15 = 'Promoplan15%.xlsx'
name_file_promo15fsm = 'Promoplan15%FSM.xlsx'

#Дополнение
name_file_honor_logo = 'logo.png'
name_file_user_ids = 'user_ids.txt'
name_file_database = 'database.json'

#Полные пути до файлов
path_name_file_allocation_12 = os.path.join(dir_files, name_file_allocation_12)
path_name_file_allocation_15 = os.path.join(dir_files, name_file_allocation_15)
path_name_file_sc = os.path.join(dir_files, name_file_sc)

path_name_file_promo12 = os.path.join(dir_files, name_file_promo12)
path_name_file_promo15 = os.path.join(dir_files, name_file_promo15)
path_name_file_promo15fsm = os.path.join(dir_files, name_file_promo15fsm)

path_name_file_honor_logo = os.path.join(dir_images, name_file_honor_logo)
path_name_file_user_ids = os.path.join(current_directory, name_file_user_ids)
path_name_file_database = os.path.join(current_directory, name_file_database)

#Подключение базы пользователей
with open(path_name_file_database, "r", encoding='utf-8') as file:
    trusted_users = json.load(file)

##########################################################################################################
def get_username_by_phone(phone_number):
    with open(path_name_file_database, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for user in data:
            if user['number'] == phone_number:
                return user['name']
    return None

def get_category_by_phone(phone_number):
    with open(path_name_file_database, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for user in data:
            if user['number'] == phone_number:
                return user['category']
    return None

def get_email_by_phone(phone_number):
    with open(path_name_file_database, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for user in data:
            if user['number'] == phone_number:
                return user['email']
    return None

#Функция по выводу меню
def menu(message, phoneUser):
    nameUser = get_username_by_phone(phoneUser)
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='\U0001F4C4 Получить файл аллокации', callback_data=f'allocation|{phoneUser}')
    button2 = types.InlineKeyboardButton(text='\U0001F5D2 Получить файл промо', callback_data=f'promo|{phoneUser}')
    button3 = types.InlineKeyboardButton(text='\U0001F6E0 Получить список АСЦ HONOR', callback_data=f'sc|{phoneUser}')
    keyboard.row(button1)
    keyboard.row(button2)
    keyboard.row(button3)
    photo = open(path_name_file_honor_logo, 'rb')
    caption = f'{nameUser}, выберите действие'
    bot.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=keyboard)

#Функция по отправке файла через электронную почту
def sendMailFile(message, nameDoc, phoneUser):
    nameDoc = os.path.basename(nameDoc)
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='\U0001F4E9 Отправить файл на email', callback_data=f'send_mail_yes:{phoneUser}:{nameDoc}')
    button2 = types.InlineKeyboardButton(text='\U0001F6AB Не отправлять', callback_data=f'send_mail_no|{phoneUser}')
    keyboard.row(button1)
    keyboard.row(button2)
    bot.send_message(message.chat.id, nameDoc, reply_markup=keyboard)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Здравствуйте!\nВведите свой номер телефона для идентификации начиная с 8 без пробелов: ")
    
    #Запись ID учатников в файл
    user_id = message.from_user.id
    with open(path_name_file_user_ids, 'a+') as file:
        file.seek(0)
        if str(user_id) not in file.read():
            file.write(str(user_id) + '\n')

    bot.register_next_step_handler(message, checkNumberUser)

def checkNumberUser(message):
    global user_data

    if message.text is not None:
        numberCheck = message.text
        user_id = message.from_user.id
        user_data[user_id] = {'phone_number': numberCheck}

        is_allowed = False

        for user in trusted_users:
            if user["number"] == numberCheck:

                phoneUser = user_data[user_id]["phone_number"]

                is_allowed = True
                break

        if is_allowed:
            menu(message, phoneUser)

        else:
            bot.send_message(message.chat.id, "Вы не зарегистрированы, доступ запрещён!")
            send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы, доступ запрещён!")
        send_welcome(message)

##################################################################################################################
#Обработка callback function
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
        try:
            if "|" in call.data:
                delimetrSlash = call.data.split('|')
                callBackData = delimetrSlash[0]
                phoneUser = delimetrSlash[1]
            elif ":" in call.data:
                delimetrTwoPoint = call.data.split(':')
                callBackData = delimetrTwoPoint[0]
                phoneUser = delimetrTwoPoint[1]
                nameDoc = delimetrTwoPoint[2]

            if callBackData == "promo":
                handle_promo(call, phoneUser)

            elif callBackData == "sc":
                handle_sc(call, phoneUser)

            elif callBackData == "allocation":
                handle_allocation(call, phoneUser)

            elif "file_allocation" in callBackData:
                handle_allocation_file(call, callBackData, phoneUser)

            elif "file_promo" in callBackData:
                handle_promo_file(call, callBackData, phoneUser)

            elif "send_mail_yes" in callBackData:
                handle_sendmail(call, phoneUser, nameDoc)
            else:
                menu(call.message, phoneUser)
        except NameError:
            send_welcome(call.message)
##################################################################################################################
#Создание функция для обработки callback_data
def handle_promo(call, phoneUser):
    categoryUser = get_category_by_phone(phoneUser)

    if categoryUser == 0:
        global f_promo_12
        global f_promo_15
        global f_promo_15fsm
        f_promo_12 = open(path_name_file_promo12, "rb")
        f_promo_15 = open(path_name_file_promo15, "rb")
        f_promo_15fsm = open(path_name_file_promo15fsm, "rb")
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='\U0001F4C4 Получить файл промо 12%', callback_data=f'file_promo_12|{phoneUser}')
        button2 = types.InlineKeyboardButton(text='\U0001F4C4 Получить файл промо 15%', callback_data=f'file_promo_15|{phoneUser}')
        button3 = types.InlineKeyboardButton(text='\U0001F4C4 Получить файл промо 15% + FSM', callback_data=f'file_promo_15fsm|{phoneUser}')
        button4 = types.InlineKeyboardButton(text='\U0001F519 Вернуться в главное меню', callback_data=f'menu|{phoneUser}')
        keyboard.row(button1)
        keyboard.row(button2)
        keyboard.row(button3)
        keyboard.row(button4)
        bot.send_message(call.message.chat.id, "Выберите кнопку:", reply_markup=keyboard)

def handle_sc(call, phoneUser):
    f_sc = open(path_name_file_sc, "rb")
    sendMailFile(call.message, path_name_file_sc, phoneUser)
    bot.send_document(call.message.chat.id, f_sc)

def handle_allocation(call, phoneUser):
    categoryUser = get_category_by_phone(phoneUser)

    if categoryUser == 12:
        f_allocation = open(path_name_file_allocation_12, "rb")
        sendMailFile(call.message, path_name_file_allocation_12, phoneUser)
        bot.send_document(call.message.chat.id, f_allocation)
    elif categoryUser == 15:
        f_allocation = open(path_name_file_allocation_15, "rb")
        sendMailFile(call.message, path_name_file_allocation_15, phoneUser)
        bot.send_document(call.message.chat.id, f_allocation)
    elif categoryUser == 0:
        global f_allocation_12
        global f_allocation_15
        f_allocation_12 = open(path_name_file_allocation_12, "rb")
        f_allocation_15 = open(path_name_file_allocation_15, "rb")
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='\U0001F4C4 Получить файл аллокации 12%', callback_data=f'file_allocation_12|{phoneUser}')
        button2 = types.InlineKeyboardButton(text='\U0001F4C4 Получить файл аллокации 15%', callback_data=f'file_allocation_15|{phoneUser}')
        button3 = types.InlineKeyboardButton(text='\U0001F519 Вернуться в главное меню', callback_data=f'menu|{phoneUser}')
        keyboard.row(button1)
        keyboard.row(button2)
        keyboard.row(button3)
        bot.send_message(call.message.chat.id, "Выберите кнопку:", reply_markup=keyboard)

def handle_allocation_file(call, callBackData, phoneUser):
    if callBackData == 'file_allocation_12':
        sendMailFile(call.message, path_name_file_allocation_12, phoneUser)
        bot.send_document(call.message.chat.id, f_allocation_12)
    elif callBackData == 'file_allocation_15':
        sendMailFile(call.message, path_name_file_allocation_15, phoneUser)
        bot.send_document(call.message.chat.id, f_allocation_15)

def handle_promo_file(call, callBackData, phoneUser):
    if callBackData == "file_promo_12":
        sendMailFile(call.message, path_name_file_promo12, phoneUser)
        bot.send_document(call.message.chat.id, f_promo_12)
    elif callBackData == "file_promo_15":
        sendMailFile(call.message, path_name_file_promo15, phoneUser)
        bot.send_document(call.message.chat.id, f_promo_15)
    elif callBackData == "file_promo_15fsm":
        sendMailFile(call.message, path_name_file_promo15fsm, phoneUser)
        bot.send_document(call.message.chat.id, f_promo_15fsm)

def handle_sendmail(call, phoneUser, nameDoc):
    # dataDelimetr = call.data.split('|')
    email = get_email_by_phone(phoneUser)
    nameDocument = nameDoc

    # Установка соединения с сервером
    smtp_server = 'smtp.yandex.ru'
    smtp_port = 25
    username = 'aleksandrhihonor@yandex.ru'
    password = 'txxjzlonbgpsvupn'

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)

    # Создание сообщения
    msg = MIMEMultipart()
    msg['Subject'] = 'HONOR'
    msg['From'] = username
    msg['To'] = email

    # Добавление текстовой части сообщения
    text_part = MIMEText('Файл во вложении')
    msg.attach(text_part)

    # Открытие файла для чтения
    file_name = nameDocument
    file_name_path = os.path.join(dir_files, file_name)

    with open(file_name_path, 'rb') as file:
        file_data = file.read()

    # Добавление файла во вложение
    attachment = MIMEApplication(file_data)
    attachment.add_header('Content-Disposition', 'attachment', filename=nameDocument)
    msg.attach(attachment)

    # Отправка сообщения
    server.send_message(msg)

    # Закрытие соединения с сервером
    server.quit()

    bot.send_message(call.message.chat.id, f"Файл отправлен на {email}")
    menu(call.message, phoneUser)

#########################################UPLOAD FILES########################################
@bot.message_handler(content_types=['document'])
def handler_document(message):

    #Создание клавиотуры для возврата в меню
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Перейти в главное меню', callback_data='startbot')
    keyboard.row(button)

    if message.chat.id == 460221344 or message.chat.id == 6531576226:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name

        if file_name == "database.json":
            path_dir = os.path.join(current_directory, file_name)
            with open(path_dir, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, f"Файл {file_name} успешно загружен на сервер!", reply_markup=keyboard)
        else:
            #Загрузка файлов на сервер в папку files
            path_dir = os.path.join(dir_files, file_name)
            with open(path_dir, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, f"Файл {file_name} успешно загружен на сервер!", reply_markup=keyboard)

        # Уведомление пользователям об обновлении файла
        with open(path_name_file_user_ids, 'r') as file:
            values = file.readlines()
            for value in values:
#                bot.send_message(460221344, value)
                if file_name == name_file_allocation_12 or file_name == name_file_allocation_15:
                    try:
                        bot.send_message(value, "Файл аллокации актуализирован!", reply_markup=keyboard)
                    except:
                        pass
                elif file_name == name_file_promo12 or file_name == name_file_promo15 or file_name == name_file_promo15fsm:
                    try:
                        bot.send_message(value, "Файл промо актуализирован!", reply_markup=keyboard)
                    except:
                        pass
                elif file_name == name_file_sc:
                    try:
                        bot.send_message(value, "Файл c информацией сервисных центров актуализирован!", reply_markup=keyboard)
                    except:
                        pass
    else:
        bot.send_message(message.chat.id, "Действие невозможно!")

#############################################################################################Запуск бота
bot.polling(none_stop=True)
