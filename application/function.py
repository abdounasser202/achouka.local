__author__ = 'wilrona'

import re
import datetime
from application import app

def datetime_convert(time): # Convertis time sous la forme YYYY-MM-DD HH:MM:SS
    _time = str(time)
    retime = re.compile(r'\W+')
    _list = retime.split(_time)

    if len(_list) >= 6:
        year = int(_list[0])
        mounth = int(_list[1])
        day = int(_list[2])
        hour = int(_list[3])
        minute = int(_list[4])
        second = int(_list[5])
        time = datetime.datetime(year, mounth, day, hour, minute, second)
        return time

    else:
        try:
            hour = int(_list[0])
            minute = int(_list[1])
            second = int(_list[2])
            time = datetime.datetime(100, 1, 1, hour, minute, second)
            return time

        except IndexError:
            hour = int(_list[0])
            minute = int(_list[1])
            time = datetime.datetime(hour, minute)
            return time


def date_convert(date):# Convertis date sous la forme YYYY-MM-DD
    _date = str(date)
    redate = re.compile(r'\W+')
    _list = redate.split(_date)
    try:
        day = int(_list[0])
        mounth = int(_list[1])
        year = int(_list[2])
        date = datetime.date(year, mounth, day)
        return date
    except ValueError:
        day = int(_list[2])
        mounth = int(_list[1])
        year = int(_list[0])
        date = datetime.date(year, mounth, day)
        return date

# jinja 2 formatage de la date
def format_date(date, format=None):
    newdate = date.strftime(format)
    return newdate


def time_convert(time): # Convertis time sous la forme HH:MM:SS
    _time = str(time)
    retime = re.compile(r'\W+')
    _list = retime.split(_time)
    try:
        hour = int(_list[0])
        minute = int(_list[1])
        second = int(_list[2])
        time = datetime.time(hour, minute, second)
        return time
    except IndexError:
        hour = int(_list[0])
        minute = int(_list[1])
        time = datetime.time(hour, minute)
        return time


def convert_in_second(time):
    if time:
        _time = str(time)
        retime = re.compile(r'\W+')
        _list = retime.split(_time)
        try:
            hour = int(_list[0]) * 3600
            minute = int(_list[1]) * 60
            second = int(_list[2])
            time = hour + minute + second
            return time
        except IndexError:
            hour = int(_list[0]) * 3600
            minute = int(_list[1]) * 60
            time = hour + minute
            return time
    else:
        time = 0
        return time


#jinja 2 ajoute du temps sur le temp en cours
def add_time(time, retard):
    time = datetime_convert(time)
    if retard:
        _time = str(retard)
        retime = re.compile(r'\W+')
        _list = retime.split(_time)
        hour = int(_list[0]) * 3600
        minute = int(_list[1]) * 60
        time2 = hour + minute
        new_time = time + datetime.timedelta(0, time2)
    else:
        new_time = time
    return new_time.time()

# jinja 2 formatage du prix avec des espaces
def format_price(price):
    return '{:,}'.format(price).replace(',', ' ')


def find(word, search):
    news = word.split(" ")
    tab = []
    tabs = []
    letter = ""

    for new in news:
        count = 0

        for n in new:
           letter += n
           tab.append(letter)
           count += 1
           if count == len(new):
               tabs.append(tab)
               count = 0
               letter = ""
               tab = []
    w = False
    for tab in tabs:
        if search in tab:
            w = True
    return w

app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['add_time'] = add_time
app.jinja_env.filters['format_price'] = format_price
