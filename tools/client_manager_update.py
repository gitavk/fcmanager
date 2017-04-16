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


# Credits.objects.all().delete()
# Contract.objects.all().delete()
# Client.objects.all().delete()

filename = sys.argv[1]
filelog = filename + '.log'
cnt = 0
total = 0

l = codecs.open(filelog, "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")

for line in f:
	total += 1
	data = line.split(",")
	lname = data[0].split(" ")[0].upper()
	fname = data[0].split(" ")[1].upper()
	clnt = Client.objects.get(last_name=lname, first_name=fname)
	mname = data[1][:-1]
	manager = User.objects.get(last_name__icontains=mname)
	clnt.manager = manager
	clnt.save()
	print clnt, manager[0].get_full_name()
	# csv.write(','.join(str(v) for v in data) + "\n")
	cnt += 1

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('success load lines: %d\r\n' % cnt)
l.write('finish\r\n')
l.close()