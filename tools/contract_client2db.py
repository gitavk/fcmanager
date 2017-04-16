#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 4 == Nastya, all other Kristina
# 11 == change contrct, 2 == year, 5-7 halfyear
import sys, os, inspect
import codecs
from datetime import date

cmd_folder = os.path.split(os.path.split(inspect.getfile( inspect.currentframe() ))[0])[0]
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")


from person.models import Client
from contract.models import Contract
from finance.models import Credits
from core.models import User
from person.forms import form_client_add
from contract.forms import form_Contract


Credits.objects.all().delete()
Contract.objects.all().delete()
Client.objects.all().delete()

filename = sys.argv[1]
csvf = "".join(filename.split(".")[:-1]) + ".csv"
filelog = filename + '.log'
cnt = 0
total = 0

l = codecs.open(filelog, "w", "utf-8")
csv = open(csvf, "w",)
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

for line in f:
	total += 1
	data = line.split("|")
	try:
		data[0] = int(data[0].strip())
		data[1] = int(data[1].strip())
		data[3] = int(data[3].strip())
		if data[3] != 3: # manager
			data[3] = 2
			#  contract_type
		data[6] = int(data[6].strip())
		if data[6] == 11:
			data[6] = 3
		elif data[6] == 2:
			pass
		else:
			data[6] = 1
		data[7] = int(data[7].strip())
		data[8] = int(data[8].strip())
	except ValueError:
		l.write('ID, NUMBER, ManagerID, contract_type_id, card, amount error in line #%d:\n' % total)
		continue

	try:
		data[11] = int(data[11].strip())
		data[12] = int(data[12].strip())
	except ValueError:
		l.write('client_id, payment_type error in line #%d:\n' % total)
		continue

	try:
		data[9] = data[9].strip()
		if len (data[9]) > 0:
			data[9] = int(data[9].strip())
			l.write('Has pay_plan_id == %d error in line #%d:\n' % (data[9], total))
		data[13] = data[13].strip()
		if len (data[13]) > 0:
			data[13] = int(data[13])
			l.write('Has discount_id == %d error in line #%d:\n' % (data[13], total))
	except ValueError:
		l.write('pay_plan_id error in line #%d:\n' % total)
		continue

	try:
		d = data[2].strip()[:10].split('-')
		data[2] = date(int(d[0]), int(d[1]), int(d[2]))
		d = data[4].strip()[:10].split('-')
		data[4] = date(int(d[0]), int(d[1]), int(d[2]))
		d = data[5].strip()[:10].split('-')
		data[5] = date(int(d[0]), int(d[1]), int(d[2]))
		d = data[10].strip()[:10].split('-')
		data[10] = date(int(d[0]), int(d[1]), int(d[2]))
	except Exception, e:
		l.write('date, date_start, date_end, payment_date error in line #%d:\n' % total)
		continue

	opendate = False
	data[14] = data[14].strip().encode('utf8')
	if data[14] not in ['t','f']:
		l.write('is_open_date error in line #%d:\n' % total)
		continue
		if data[14] == 't':
			opendate = True

	# client fields
	try:
		data[15] = int(data[15].strip())
		data[19] = int(data[19].strip())
		data[23] = int(data[23].strip())

		data[26] = int(data[26].strip())
		if data[26] != 3:# manager
			data[26] = 2
	except ValueError:
		l.write('ID, gender, phone, manager_id error in line #%d:\n' % total)
		continue

	try:
		d = data[20].strip()[:10].split('-')
		data[20] = date(int(d[0]), int(d[1]), int(d[2]))
	except Exception, e:
		l.write('born_date, error in line #%d:\n' % total)
		continue

	data[16] = data[16].strip().encode('utf8')
	data[17] = data[17].strip().encode('utf8')
	data[18] = data[18].strip().encode('utf8')
	data[21] = data[21].strip().encode('utf8')
	data[22] = data[22].strip().encode('utf8')
	data[24] = data[24].strip().encode('utf8')
	data[25] = data[25].strip().encode('utf8')

	cltdata = {'first_name' : data[16],
			   'last_name' : data[17],
			   'patronymic' : data[18],
			   'gender' : data[19],
			   'born_date' : data[20],
			   'avatar' : data[21],
			   'address' : data[22],
			   'is_online' : False,
			   'phone' : data[23],
			   'email' : data[24],
			   'passport' : data[25],
			   'manager' : data[26],
			   'address' : data[22]
			   }
	form = form_client_add(cltdata)
	if form.is_valid():
		cl = form.save()

	cndata = {'number' : data[1],
			   'date' : data[2],
			   'manager' : data[3],
			   'date_start' : data[4],
			   'date_end' : data[5],
			   'contract_type' : data[6],
			   'card' : data[7],
			   'amount' : data[8],
			   'pay_plan' : '',
			   'payment_date' : data[10],
			   'client': cl.pk,
			   'payer': cl.pk,

			   'discount' : data[13],
			   'is_open_date' : opendate,
			   'is_current' : 2,
			   'payment_type' : data[12]
		}
	fc = form_Contract(cndata)
	if fc.is_valid():
		fc.save()
	# print data
	# csv.write(','.join(str(v) for v in data) + "\n")
	cnt += 1

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('success load lines: %d\r\n' % cnt)
l.write('finish\r\n')
l.close()
csv.close()