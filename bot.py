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
    lock = Lock()
    lock.acquire()
    try:
        write_start_date(str(message.chat.id), our_date)
    finally:
        lock.release()
    if not check_valid_date(our_date):
        bot.send_message(message.from_user.id, "Извините, произошла ошибка. \n"+
                         "Введите корректную дату в формате YYYY-MM-DD /date.")
    elif check_change_date(str(message.chat.id),our_date):
        bot.send_message(message.from_user.id, "Дата не изменилась поиск продолжается по той же дате, приятного пользования.\n")
    else:
        start_thread(message, lock)

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


def write_each_date(user, date):
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        result[user][1] = date
        result[user][2] = ""#date
    with open("result.json", "w") as f:
        f.write(json.dumps(result))

def start_thread(message, lock):
    date = message.text
    bot.send_message(message.from_user.id, "Установлена новая дата " + message.text)
    lock.acquire()
    try:
        write_each_date(str(message.chat.id), str(message.text))
    finally:
        lock.release()
    th1 = Thread(target=parse.check_free_date, args=(str(message.chat.id), date, lock))
    th2 = Thread(target=check_date, args=(message, date, lock))
    th1.start()
    th2.start()
    th1.join()
    th2.join()


def read_date(user):
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        return (result[user][1], result[user][2])

def check_date(message, our_date, lock):
    while True:
        time.sleep(5)
        lock.acquire()
        try:
            date, result_date = read_date(str(message.chat.id))
            if our_date != date:
                write_result_date(str(message.chat.id), "", False)
                break
            elif result_date != "":
                bot.send_message(message.from_user.id, "Ура, освободивась новая дата " + result_date)
                bot.send_message(message.from_user.id, "Поставте новую дату /date")
                write_result_date(str(message.chat.id), "", True)
                break
        finally:
            lock.release()



def write_result_date(user, date, flag):
    """
    :param user: str
    :param date: str
    :param flag: bool, для записи, что нашли дату.
    :return:
    """
    result = ""
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        result[user][2] = date
        if flag:
            result[user][1] = "1970-01-01 "
    with open("result.json", "w") as f:
        f.write(json.dumps(result))


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



if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except Exception as e:
            time.sleep(3)
            config.write_log(e)

