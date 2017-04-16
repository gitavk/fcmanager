# -*- coding: utf-8 -*-
import os
import urllib2
from decimal import Decimal
import cgi, cgitb

print "Content-type: text/html\n\n";
print "\n";

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
chtype = form.getvalue('chtype')
sales = form.getvalue('sales')
sales = urllib2.unquote(sales.encode('utf-8'))
clnt = form.getvalue('clnt')
if clnt:
        clnt = urllib2.unquote(clnt.encode('utf-8'))
else:
        clnt = ''

try:
        sales = sales.split('|')
except Exception:
        print 'error'
callback = form.getvalue('callback')
summ = 0

f = open("returnsale.vbs", "w")
f.write('Dim Shtrih\n')
f.write('Set Shtrih = CreateObject("AddIn.DrvFR")\n')
f.write('Shtrih.connect()\n')
f.write('Shtrih.CheckType=2\n')
f.write('Shtrih.OpenCheck()\n')
if len(clnt.decode('utf8').encode('cp1251').strip() ) > 0:
        g = clnt.decode('utf8').encode('cp1251')[0:39]
        f.write('Shtrih.StringForPrinting="%s"\n' % g)
        f.write('Shtrih.PrintString()\n')

for x in range(0,(len(sales)-1)/5):
    g = (sales[x*5+1]).decode('utf8').encode('cp1251')[0:39]
    f.write('Shtrih.StringForPrinting="%s"\n' % g)
    # quantity always equal 1
    q = 1
    f.write('Shtrih.Quantity=%d\n' % q)
    p = Decimal(sales[x*5+3].replace(',','.'))
    f.write('Shtrih.Price=%d\n' % p)
    d = int(sales[x*5+4])
    f.write('Shtrih.Department=%d\n' % d)
    summ += q * p
    f.write('Shtrih.ReturnSale()\n')
    
f.write('Shtrih.StringForPrinting=""\n')
f.write('Shtrih.Summ%s=%d\n' % (chtype, summ))
f.write('Shtrih.CloseCheck()\n')
f.write('Shtrih.GetECRStatus()\n')
f.write('WScript.StdOut.Write(Shtrih.ECRMode)\n')
f.write('WScript.Quit (0)')
f.close()

p = os.popen("wscript returnsale.vbs").read()

# if d == 1:
#         cp = os.popen("wscript RepeatDocument.vbs").read()

print  '%s({"res" : "%s"})' % (callback, p)
