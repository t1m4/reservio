import requests
import time
import re
import urllib
import datetime
import json
import config



def change_url(url):
    """
    :param url: str
    :return:  str
    """
    now = datetime.datetime.now()
    change = datetime.timedelta(days=31)
    next_month = now + change
    url = url.replace("from%5D=2020-07-1","from%5D="+now.strftime("%Y-%m-%d"))
    url = url.replace("to%5D=2020-07-20","to%5D="+next_month.strftime("%Y-%m-%d"))
    return url

def load_date():
    """
    :param url: str
    :return: dict
    """
    url = config.URL
    url = change_url(url)
    return json.loads(requests.get(url).text)


def check_free_date(bot, message):
    """
    :param our_date: str
    :return: str
    """
    user = str(message.chat.id)
    our_date = str(message.text)
    while True:
        time.sleep(1)
        try:
            date = read_date(user)
            if our_date != date:
                    write_result_date(user, "", False)
                    break
            data_list = load_date()["data"]
            for data in data_list:
                if data['attributes']["isAvailable"] == True:
                    if compare_date(our_date, data['attributes']["date"]):
                        bot.send_message(message.from_user.id, "Ура, освободивась новая дата " + data['attributes']["date"])
                        bot.send_message(message.from_user.id, "Поставте новую дату /date")
                        write_result_date(user, data['attributes']["date"], True)
                        return ""
                    else:
                        break

        except Exception as e:
            config.write_log(e)
            continue

def read_date(user):
    """
    :param user: str
    :return: str
    """
    with open("result.json", "r") as f:
        result = json.loads(f.read())
        return result[user][1]
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

def compare_date(our_date, date):
    '''
    :param our_date:
    :param date:
    :return: bool
    '''
    our_year, our_month, our_day = our_date.split("-")
    year, month, day = date.split("-")
    if int(year) < int(our_year) or int(year) == int(our_year) and int(month) < int(our_month) or int(year) == int(our_year) and int(month) == int(our_month) and int(day) < int(our_day):
            return True
    return False




