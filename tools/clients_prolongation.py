#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, inspect
import codecs
from datetime import datetime, date, timedelta
# add project dir to sys path
cmd_folder = os.path.split(os.path.split(inspect.getfile( inspect.currentframe() ))[0])[0]
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")

from person.models import Client
from contract.models import Contract, ContractType
from core.models import User

filename = sys.argv[1]
filelog = filename + '.log'
cnt = 0
total = 0

# Guest.objects.all().delete()

l = codecs.open(filelog, "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

ct = ContractType.objects.get(pk=3) # pereoformlenie
last_day = date(2014, 5, 1)
manager = User.objects.get(pk=3)

for line in f:
	total += 1
	data = line.split(',')
	born = data[8].split('/')
	if len (born) > 2:
		born = date(int(born[2]), int(born[0]), int(born[1]), )
		fullname = data[6].strip().upper().split()
		first_name = fullname[1]
		last_name = fullname[0]
		patronymic = fullname[2]

		phone = data[7].split(' ')[0]
		if len(phone) == 7:
			try:
				p = int(phone)
			except Exception, e:
				phone = '9999999'
			phone = '812' + phone
		elif len(phone) == 10:
			try:
				p = int(phone)
			except Exception, e:
				phone = '0000999999'
			if int(phone[:3]) == 812:
				phone = phone
			elif int(phone[0]) == 9:
				phone = '7' + phone
			else:
				l.write('error phone prefix "%s" in line #%d: %s\r' % (int(phone[:3]),total, line))
		elif len(phone) == 11:
			try:
				p = int(phone)
			except Exception, e:
				l.write('error phone "%s" in line #%d: %s\r' % (phone,total, line))
				phone = '00009999999'
			if int(phone[1]) == 9:
				phone = '7' + phone[1:]
			else:
				l.write('error phone "%s" in line #%d: %s\r' % (phone,total, line))

		try:
			clnt = Client.objects.get(first_name__iexact=first_name,
									 last_name__iexact=last_name,
									  born_date=born,
									  patronymic__iexact=patronymic)
			print 'Old: ', patronymic , last_name, first_name
		except Client.DoesNotExist:
			print 'New: ', patronymic , last_name, first_name
			clnt = Client(first_name=first_name, last_name=last_name,
						  born_date=born, patronymic=patronymic,
						  phone=phone, manager=manager)
			clnt.save()
			# clntsave += 1
		finish_date = data[3].split('/')
		finish_date = date(int(finish_date[2]), int(finish_date[0]), int(finish_date[1]), )
		rest_days = (finish_date - last_day).days
		# print datetime.now().date() + timedelta(days=rest_days)
		if rest_days < 1:
			print rest_days
		cnumber = int(data[1])
		try:
			c = Contract.objects.get(number=cnumber, client=clnt)
			c.date_start = datetime.now().date()
			c.date_end = datetime.now().date() + timedelta(days=rest_days)
		except Contract.DoesNotExist:
			c = Contract(number=cnumber, client=clnt, payer=clnt,
						manager=manager, date_start=datetime.now().date(),
						date_end=datetime.now().date() + timedelta(days=rest_days),
						contract_type=ct, card=0, amount=0, payment_date=datetime.now(),
						payment_type=2, is_current=2
						)

		c.save()

		# print patronymic , last_name, first_name, phone

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('success load lines: %d\r\n' % cnt)
l.write('finish\r\n')
l.close()