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
from contract.models import Contract

filename = sys.argv[1]
filelog = filename + '.log'
cnt = 0
total = 0

td = datetime.today().date()

l = codecs.open(filelog, "w", "utf-8")
al = codecs.open(filename+'is_act_', "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

managers = {}
fmanagers = codecs.open('master_managers.csv','r',"utf-8")
for line in fmanagers:
	data = line.split(',')
	mname = data[0].strip().upper()
	managers[mname] = int(data[1])
fmanagers.close()
activecontracts = 0
clntsave = 0

for line in f:
	total += 1
	active = 0
	amount = 0
	b_date = []
	card = ""
	data = line.split(';')
	full_name = data[12].split(' ')
	if len (full_name) < 2:
		continue

	lname = full_name[0].strip().upper()
	fname = full_name[1].strip().upper()
	if len(full_name) < 3:
		pname = '..'
	else:
		pname = full_name[2].strip().upper()
	# print fname, sname, pname
	b_date = data[14].strip().split('/')
	if len (b_date) > 2: # born
		try:
			b_date = date(int(b_date[2]), int(b_date[0]), int(b_date[1]), )
		except Exception, e:
			l.write('Wrong born "%s" in line #%d: %s\r' % (data[14], total, line))
			continue
	else:
		l.write('Wrong born "%s" in line #%d: %s\r' % (data[14], total, line))
		continue
		
	manager = data[37].upper()
	# if not manager in managers:
	# 	managers.append(manager)
	# print manager
	try:
		manager_id = managers[manager]
	except KeyError:
		l.write('unknown manager "%s" in line #%d: %s\r' % (manager, total, line))
		continue
	
	try:
		manager = User.objects.get(pk=manager_id)
	except User.DoesNotExist:
		l.write('unknown manager "%s" in line #%d: %s\r' % (manager, total, line))
		continue

	r_date = data[1].split('/') # contract start
	if len (r_date) > 2:
		r_date = date(int(r_date[2]), int(r_date[0]), int(r_date[1]), )

	# print ("first_name='%s', last_name='%s', patronymic='%s'" % (fname, lname, pname))
	# print b_date
	try:
		clnt = Client.objects.get(first_name=fname, last_name=lname,
							born_date=b_date, patronymic=pname)
	except Client.DoesNotExist:
		continue

	clnt.manager = manager
	clnt.save()
	clntsave += 1

	try:
		contract = Contract.objects.get(client=clnt, date=r_date)
	except Exception, e:
		continue
	contract.number = data[2].strip()
	contract.save()
	activecontracts += 1

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('Contracts update: %d\r\n' % activecontracts)
l.write('Clients update: %d\r\n' % clntsave)
l.write('finish\r\n')
al.close()
l.close()