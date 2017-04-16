#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import urllib2
import time
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
        tdelta = os.popen("echo 'CheckDate\n' >> cashier.log").read()
        if tdelta > 60:
                r = os.popen("echo 'logSyncDate\n' >> cashier.log").read()
        p = os.popen("echo 'OpenSession\n' >> cashier.log").read()
elif action == 'z':
        # Отчет по отделам
        # p = subprocess.Popen("echo 'PrintDepartmentReport\n' >> cashier.log", shell=True, stdout=subprocess.PIPE)
        p = subprocess.Popen("cat /home/avk/old/user.bak.tar.bz2 > dump", shell=True, stdout=subprocess.PIPE)
        p.wait()
        # Отчет с гашением
        p = os.popen("echo 'PrintReportWithCleaning\n' >> cashier.log").read()
elif action == 'x':
        # Отчет без гашения
        p = os.popen("echo 'PrintReportWithoutCleaning\n' >> cashier.log").read()
else:
        p = '-1000'

print  '%s({"res" : "%s"})' % (callback, p)