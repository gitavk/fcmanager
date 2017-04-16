#! /usr/bin/python
# -*- coding: utf-8 -*-
import cgi

form = cgi.FieldStorage()

callback = form.getvalue('callback')

print "Content-type: text/html\n\n";
print "\n";
print  '%s({"res" : "%s"})' % (callback, 0)