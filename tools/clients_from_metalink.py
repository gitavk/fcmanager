#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, inspect
import codecs
from datetime import datetime, date
# add project dir to sys path
cmd_folder = os.path.split(os.path.split(inspect.getfile( inspect.currentframe() ))[0])[0]
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")

from person.models import Client
from core.models import User
from finance.models import Credits, Client_PTT
from contract.models import Contract, ContractType

filename = sys.argv[1]
filelog = filename + '.log'
cnt = 0
total = 0

Client_PTT.objects.all().delete()
Credits.objects.all().delete()
Contract.objects.all().delete()
Client.objects.all().delete()

td = datetime.today().date()

l = codecs.open(filelog, "w", "utf-8")
al = codecs.open(filename+'is_act_', "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

# managers = {}
# fmanagers = codecs.open('managers.csv','r',"utf-8")
# for line in fmanagers:
# 	data = line.split(',')
# 	mname = data[0].strip().upper()
# 	managers[mname] = int(data[1])
# fmanagers.close()

contracts = {}
fcontracts = codecs.open('contracts.csv','r',"utf-8")
for line in fcontracts:
	data = line.split(',')
	mname = data[0].strip().upper()
	if data[1]:
		contracts[mname] = int(data[1])
fcontracts.close()

activecontracts = 0
clntsave = 0

for line in f:
	total += 1
	active = 0
	amount = 0
	b_date = []
	card = ""
	data = line.split(';')
	full_name = data[0].split(' ')
	if len (full_name) < 2:
		continue

	lname = full_name[0].strip().upper()
	fname = full_name[1].strip().upper()
	if len(full_name) < 3:
		pname = '..'
	else:
		pname = full_name[2].strip().upper()
	# print fname, sname, pname
	b_date = data[42].strip().split('/')
	if len (b_date) > 2: # born
		try:
			b_date = date(int(b_date[2]), int(b_date[0]), int(b_date[1]), )
		except Exception, e:
			l.write('Wrong born "%s" in line #%d: %s\r' % (data[42], total, line))
			continue
	else:
		l.write('Wrong born "%s" in line #%d: %s\r' % (data[42], total, line))
		continue
		
	# print phone
	address = ' '.join(data[41].split(' ')[1:])
	# print address
	# manager = data[22].upper()
	# if not manager in managers:
	# 	managers.append(manager)
	# print manager
	manager_id = 1
	try:
		manager = User.objects.get(pk=manager_id)
	except User.DoesNotExist:
		l.write('unknown manager "%s" in line #%d: %s\r' % (manager, total, line))
		continue

	s_date = data[5].split('/') # contract start
	if len (s_date) > 2:
		s_date = date(int(s_date[2]), int(s_date[0]), int(s_date[1]), )
	e_date = data[6].split('/') # contract start
	if len (e_date) > 2:
		e_date = date(int(e_date[2]), int(e_date[0]), int(e_date[1]), )
	# print s_date, e_date

	cname = data[8].strip().upper()
	# if not cname in contracts:
	# 	contracts.append(cname)
	if s_date <= td and td <= e_date:
		# print fname, sname, pname
		active = 1
		r_date = data[2].split('/')
		if len (r_date) > 2:
			r_date = datetime(int(r_date[2]), int(r_date[0]), int(r_date[1]), )
		else:
			r_date = td
		ct_id = contracts[cname]
		try:
			contract_type = ContractType.objects.get(pk=ct_id)
		except ContractType.DoesNotExist:
			l.write('unknown ContractType "%s" in line #%d: %s\r' % (cname, total, line))
			active = 0
		try:
			card = int(data[3])
		except Exception, e:
			l.write('Wrong card number "%s" in line #%d: %s\r' % (data[3], total, line))
			card = 0
		try:
			amount = float(data[16].replace(',',''))
		except Exception, e:
			l.write('Wrong amount "%s" in line #%d: %s\r' % (data[16], total, line))
			amount = 0

	phone = data[41].split(' ')[0]
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

	# print ("first_name='%s', last_name='%s', patronymic='%s'" % (fname, lname, pname))
	# print b_date
	try:
		clnt = Client.objects.get(first_name=fname, last_name=lname,
							born_date=b_date, patronymic=pname)
	except Client.DoesNotExist:
		clnt = Client(first_name=fname, last_name=lname,
					  born_date=b_date, patronymic=pname,
					  address=address, phone=phone,
					  manager=manager)
		clnt.save()
		clntsave += 1

	if active:
		try:
			cnumber = Contract.objects.latest()
			cnumber = cnumber.pk + 1
		except Contract.DoesNotExist:
			cnumber = 1
		cnumber = u'm' + str(cnumber)
		print cnumber, r_date, amount, card
		ct = Contract(number=cnumber, date=r_date, manager=manager,
			date_start=s_date, date_end=e_date, contract_type=contract_type,
			card=card, amount=amount, payment_date=r_date, client=clnt,
			payer=clnt, is_current=1, payment_type=2)
		ct.save()
		activecontracts += 1

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('active contracts load: %d\r\n' % activecontracts)
l.write('Clients add: %d\r\n' % clntsave)
l.write('finish\r\n')
al.close()
l.close()