#!/usr/bin/env python
import os, sys, inspect
from datetime import datetime, timedelta

# add project dir to sys path
cmd_folder = os.path.split(os.path.split(inspect.getfile( inspect.currentframe() ))[0])[0]
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")

from finance.models import *

# activate Price by date_start
for p in Price.objects.filter(date_start__lte=datetime.now().date(),
								date_end__isnull=True,
								is_active=0):
	#  deactivate old price
	old_price = Price.objects.get(goods=p.goods, 
								date_end=p.date_start,
								is_active=-1)
	old_price.is_active = old_price.id
	old_price.save()
	#  activate current price
	p.is_active = -1
	p.save()