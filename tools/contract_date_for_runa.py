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
filelog = filename + '-log.csv'
cnt = 0
total = 0
activecontracts = 0
wrong_data = 0
clntsave = 0

td = datetime.today().date()

l = codecs.open(filelog, "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

for line in f:
	total += 1
	active = 0
	amount = 0
	data = line.split(';')
	
	s_date = data[3].split('/') # contract start
	if len (s_date) > 2:
		s_date = date(int(s_date[2]), int(s_date[0]), int(s_date[1]), )
	e_date = data[4].split('/') # contract end
	if len (e_date) > 2:
		e_date = date(int(e_date[2]), int(e_date[0]), int(e_date[1]), )
	else:
		wrong_data += 1
		# l.write('Wrong data;%s;%s;%s\n' % 
		# 		(e_date, ' '.join(full_name), cname)
		# 	   )
		continue
	cnumber = data[2].strip()
	if e_date > td:
		try:
			c = Contract.objects.get(number=cnumber)
			c.date_start = s_date
			c.date_end = e_date
			c.save()
			activecontracts += 1
		except ContractType.DoesNotExist:
			l.write('Contract not found;%s;%s\n' % (cname, ' '.join(full_name)))
			continue

		# l.write('contract: %s ' % cname)
		# l.write('full_name: %s\n' % ''.join(full_name))

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('wrong data: %d\r\n' % wrong_data)
l.write('active contracts load: %d\r\n' % activecontracts)
l.write('Clients add: %d\r\n' % clntsave)
l.write('finish\r\n')
l.close()