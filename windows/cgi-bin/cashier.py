# -*- coding: utf-8 -*-
import os
import urllib2
import time
from decimal import Decimal
import cgi, cgitb

print "Content-type: text/html\n\n";
print "\n";

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
action = form.getvalue('action')
callback = form.getvalue('callback')

if action == 'session':
        #check date
        tdelta = os.popen("wscript CheckDate.vbs").read()
        if tdelta > 60:
                r = os.popen("wscript SyncDate.vbs").read()
        p = os.popen("wscript OpenSession.vbs").read()
elif action == 'd':
        # Отчет по отделам
        p = os.popen("wscript PrintDepartmentReport.vbs").read()
        time.sleep(3)
elif action == 'z':
        # Отчет с гашением
        p = os.popen("wscript PrintReportWithCleaning.vbs").read()
elif action == 'x':
        # Отчет без гашения
        p = os.popen("wscript PrintReportWithoutCleaning.vbs").read()
else:
        p = '-1000'

print  '%s({"res" : "%s"})' % (callback, p)
