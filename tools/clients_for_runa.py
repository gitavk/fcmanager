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

# Client_PTT.objects.all().delete()
# Credits.objects.all().delete()
# Contract.objects.all().delete()
# Client.objects.all().delete()

td = datetime.today().date()

l = codecs.open(filelog, "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

for line in f:
	total += 1
	active = 0
	amount = 0
	data = line.split(';')
	full_name = data[12].split(' ')
	born = data[14].split('/') # client born
	if len (born) > 2:
		born = date(int(born[2]), int(born[0]), int(born[1]), )

	cname = data[7]
	cname = cname.strip()
	cdate = data[1].split('/') # contract data
	if len (cdate) > 2:
		cdate = date(int(cdate[2]), int(cdate[0]), int(cdate[1]), )
	else:
		continue			
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

	if total > 1 and e_date > td:
		activecontracts += 1
		try:
			ct = ContractType.objects.get(name__iexact=cname, is_active=True)
		except ContractType.DoesNotExist:
			l.write('Unnown contract;%s;%s\n' % (cname, ' '.join(full_name)))
			continue

		cts = ContractType.objects.filter(name__iexact=cname).order_by('-date_modified')

		if type(born) == list:
			l.write('Wrong born date;%s;%s;%s\n' % 
					(e_date, ' '.join(full_name), born)
					)
			continue
		else:
			try:
				cl = Client.objects.get(first_name__iexact=full_name[1],
										last_name__iexact=full_name[0],
										patronymic__iexact=full_name[2],
										born_date=born,
										)
				try:
					cl_ct = Contract.objects.get(contract_type__in=cts,
											 	 date__day=cdate.day,
											 	 date__year=cdate.year,
											 	 date__month=cdate.month,
											 	 client=cl)
				except Contract.DoesNotExist:
					cl_ct = Contract(contract_type=cts[0],
							 date_start=s_date, date_end=e_date,
						     date=cdate, client=cl, payer=cl,
						     payment_date=cdate, number=data[2].strip(),
						     amount=cts[0].price,
						     manager=User.objects.get(pk=10))
					try:
						cl_ct.save()
					except Exception, e:
						print e
					
					l.write('Contract add;%s;%s;%s\n' % 
							(cdate, cname, ' '.join(full_name))
						   )
			except Client.DoesNotExist:
				phone = data[13].strip()
				if len(phone) == 7:
					phone = '812' + phone
				elif len(phone) == 10:
					if int(phone[:3]) == 812:
						phone = phone
					elif int(phone[0]) == 9:
						phone = '7' + phone
					else:
						l.write('error phone prefix "%s" in line #%d: %s\r' % (int(phone[:3]),total, line))
						continue
				elif len(phone) == 11:
					try:
						p = int(phone)
					except Exception, e:
						l.write('error phone "%s" in line #%d: %s\r' % (phone,total, line))
						continue
					if int(phone[1]) == 9:
						phone = '7' + phone[1:]
				l.write('New client;%s;%s;%s;%s\n' % 
							(born, ' '.join(full_name), cname, e_date)
						)
				cl = Client(first_name=full_name[1],
							last_name=full_name[0],
							patronymic=full_name[2],
							born_date=born, phone=phone,
							manager=User.objects.get(pk=10))
				cl.save()
				cl_ct = Contract(contract_type=cts[0],
								 date_start=s_date, date_end=e_date,
								 date=cdate, client=cl, payer=cl,
						     	 amount=cts[0].price, number=data[2].strip(),
						     	 payment_date=cdate,
								 manager=User.objects.get(pk=10))
				try:
					cl_ct.save()
				except Exception, e:
					print e
				clntsave += 1
			except IndexError:
				l.write('Wrong patronymic;%s;%s;%s\n' % 
							(e_date, ' '.join(full_name), cname)
						)

		# l.write('contract: %s ' % cname)
		# l.write('full_name: %s\n' % ''.join(full_name))

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('wrong data: %d\r\n' % wrong_data)
l.write('active contracts load: %d\r\n' % activecontracts)
l.write('Clients add: %d\r\n' % clntsave)
l.write('finish\r\n')
l.close()