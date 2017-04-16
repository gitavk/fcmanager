#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, inspect
import codecs
from datetime import datetime
# add project dir to sys path
cmd_folder = os.path.split(os.path.split(inspect.getfile( inspect.currentframe() ))[0])[0]
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")

from organizer.models import Guest
from core.models import User
from organizer.forms import FormGuest

filename = sys.argv[1]
filelog = filename + '.log'
cnt = 0
total = 0

# Guest.objects.all().delete()

l = codecs.open(filelog, "w", "utf-8")
l.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")
for line in f:
	total += 1
	data = line.split(',')
	gdate = data[0].split('/')
	if len (gdate) > 2:
		gdate = datetime(int(gdate[2]), int(gdate[0]), int(gdate[1]), )
		phone = data[2].strip()
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
			else:
				l.write('error phone "%s" in line #%d: %s\r' % (phone,total, line))
				continue
		else:
			l.write('error phone length in line #%d: %s\r' % (total, line))
			continue
		try:
			g = Guest.objects.get(phone=int(phone))
		except Exception, e:
			g = 0
		if g != 0:
			l.write(u'Guest с таким Phone уже существует. #%d: %s\r' % (total, line))
			l.write(u'Дата:%s/%s/%s Менеджер:%s .\r\n' % (g.date.day, g.date.month, g.date.year, g.manager,))
			continue
		name = data[1].strip()[:30]
		if len(data) > 3:
			note = data[3].strip()
		else:
			note = ""

		guestdata = {'date' : gdate,
				 'first_name' : name,
				 'phone' : phone,
				 'gtype' : 0,
				 'manager' : 3,
				 'is_client' : 0}
		form = FormGuest(guestdata)
		if form.is_valid():
			form.save()
			cnt += 1
		else:
			info = ""
			for field, errors in form.errors.items():
				for e in errors:
					info += e
			l.write('Database error:"%s" in line #%d: %s\r' % (info, total, line))
	else:
		l.write('error dateformat in line #%d: %s\r' % (total, line))

f.close()
l.write('total read lines: %d\r\n' % total)
l.write('success load lines: %d\r\n' % cnt)
l.write('finish\r\n')
l.close()