# -*- coding: utf-8 -*-
from datetime import date

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&bh9dvy7&w)i)oibeigll9ioz1x&zb5j$_)8)4l1@6e8a60q8j'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'DBNAME',
        'USER': 'DBUSER',
        'PASSWORD': 'PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

FCLUB_NAME = 'test'
PTT_START = 700
CNUMBERDELTA = 179
CASHIER_HOST = 'localhost'
DEPARTMENTS = range(1, 17)
ABC = (u"А", u"Б", u"В", u"Г", u"Д", u"Е", u"Ё", u"Ж", u"З", u"И", u"К",
       u"Л", u"М", u"Н", u"О", u"П", u"Р", u"С", u"Т", u"У", u"Ф", u"Х",
       u"Ц", u"Ч", u"Ш", u"Щ", u"Э", u"Ю", u"Я",)
REPORT_TOP_PREFIX = u"Генеральный директор ООО 'ВВВ'\n"
REPORT_TOP_PREFIX += u"___ Аааа Д.Е."

# set the params in NONE for already working application
CLOSE_DAY = date(2018, 6, 30)
OPEN_DAY = date(2018, 12, 26)
