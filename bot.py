#!/usr/bin/python
import telebot
import time
import parse
import config
import re
from threading import Thread, Lock
import datetime
import json


bot = telebot.TeleBot(config.TOKEN)




@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        bot.send_message(
            message.chat.id,
            'Привет, я твой бот и я помогу тебе.\n' +
            'Для того чтобы установить или поменять дату нажмите /date.\n' +
            'Для прочтения возможностей и получения помощи /help.\n'
        )
        if message.chat.id != config.main_id:
            bot.send_message(config.main_id, "Start new user " + str(message.chat.id))
    except Exception as e:
        config.write_log(e)

@bot.message_handler(commands=['help'])
def help_command(message):
    try:
        bot.send_message(
            message.chat.id,
            'Вот мои возможности:\n' +
            '1. Команда для старта /start\n' +
            '2. Команда для установки или изменения даты /date. Записывается в формате YYYY-MM-DD.\n' +
            'Для обращения к разработчику @python_8'
        )
    except Exception as e:
        config.write_log(e)

@bot.message_handler(commands=['date'])
def date_command(message):
    print(message.chat.id, "date")
    date = read_user_date(str(message.chat.id))
    try:
        bot.send_message(message.from_user.id, 'На данный момент стоит дата '+date+"\nНапишите новую дату в формате YYYY-MM-DD");
        bot.register_next_step_handler(message, get_our_date)
    except Exception as e:
        config.write_log(e)

def read_user_date(user):
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        if result.get(user) == None:
            return "1970-01-01"
        else:
            return result[user][1]


def get_our_date(message):
    our_date = message.text
    write_start_date(str(message.chat.id), our_date)
    if not check_valid_date(our_date):
        bot.send_message(message.from_user.id, "Извините, произошла ошибка. \n"+
                         "Введите корректную дату в формате YYYY-MM-DD /date.")
    elif check_change_date(str(message.chat.id),our_date):
        bot.send_message(message.from_user.id, "Дата не изменилась поиск продолжается по той же дате, приятного пользования.\n")
    else:
        start_thread(message)

def write_start_date(user, date):
    '''
    :param user: str
    :param date: str
    :return:
    '''
    result = ""
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        if result.get(user) == None :
            result[user] = [[date]]
            result[user].append("1970-01-01")
            result[user].append("")
        else:
            result[user][0].append(date)
    with open("result.json", "w") as f:
        f.write(json.dumps(result))
    with open("date.txt", "a") as file:
        file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +" " + str(user) + " " + date +"\n")

def check_valid_date(date):
    """
    :param date: str
    :return: bool
    """
    result = re.search("(\d\d\d\d)-(\d\d)-(\d\d)", date)
    result = "None" if (result == None) else result
    if result == "None" or int(result.group(2)) > 12 or int(result.group(3)) > 31:
        return False
    return True

def check_change_date(user, date):
    """
    :param user: srt
    :param date: str
    :return: bool
    """
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        if date == result[user][1]:
            return True


def write_each_date(user, date):
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        result[user][1] = date
    with open("result.json", "w") as f:
        f.write(json.dumps(result))

def start_thread(message):
    bot.send_message(message.from_user.id, "Установлена новая дата " + message.text)
    write_each_date(str(message.chat.id), str(message.text))
    th1 = Thread(target=parse.check_free_date, args=(bot, message, ))
    th1.start()


if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except Exception as e:
            time.sleep(3)
            config.write_log(e)

