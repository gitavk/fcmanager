#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import codecs
from datetime import datetime, date

# add project dir to sys path
cmd_folder = os.path.split(os.path.split(inspect.getfile(inspect.currentframe()))[0])[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fclub.settings")

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
close_day = date(2018, 6, 30)
open_day = date(2018, 12, 26)
td = datetime.today().date()

log_f = codecs.open(filelog, "w", "utf-8")
log_f.write('start upload: %s \n' % filename)
f = codecs.open(filename, "r", "utf-8")
unknown_contracts = set()
manager = User.objects.filter(groups__name='manager').order_by('id')[0]

for line in f:
    total += 1
    active = 0
    amount = 0
    data = line.split(';')
    full_name = data[12].split(' ')
    born = data[14].split('/')  # client born
    if len(born) > 2:
        born = date(int(born[2]), int(born[0]), int(born[1]), )
    cname = data[7]
    cname = cname.strip()
    cdate = data[1].split('/')  # contract data
    if len(cdate) > 2:
        cdate = date(int(cdate[2]), int(cdate[0]), int(cdate[1]), )
    else:
        continue
    s_date = data[3].split('/')  # contract start
    if len(s_date) > 2:
        s_date = date(int(s_date[2]), int(s_date[0]), int(s_date[1]), )
    e_date = data[4].split('/')  # contract end
    if len(e_date) > 2:
        e_date = date(int(e_date[2]), int(e_date[0]), int(e_date[1]), )
        if e_date < close_day:
            log_f.write(
                'Contract is ended: %s;%s;%s\n' %
                (e_date, ' '.join(full_name), cname)
            )
            continue
        e_date = open_day + (e_date - close_day)
    else:
        wrong_data += 1
        log_f.write(
            'Wrong data;%s;%s;%s\n' %
            (e_date, ' '.join(full_name), cname)
        )
        continue
    if total > 1 and e_date > td:
        activecontracts += 1
        try:
            ct = ContractType.objects.get(name__iexact=cname, is_active=True)
        except ContractType.DoesNotExist:
            unknown_contracts.add(cname)
            log_f.write('Unknown contract;%s;%s\n' % (cname, ' '.join(full_name)))
            continue
        cts = ContractType.objects.filter(name__iexact=cname).order_by('-date_modified')

        if not isinstance(born, date):
            log_f.write(
                'Wrong born date;%s;%s;%s\n' %
                (e_date, ' '.join(full_name), born)
            )
            continue
        else:
            try:
                cl = Client.objects.get(
                    first_name__iexact=full_name[1],
                    last_name__iexact=full_name[0],
                    patronymic__iexact=full_name[2],
                    born_date=born,
                    # pk=-1,
                )
                log_f.write('old client: name %s\n' % cl.get_full_name())
                try:
                    cl_ct = Contract.objects.get(contract_type__in=cts,
                                                 date__day=cdate.day,
                                                 date__year=cdate.year,
                                                 date__month=cdate.month,
                                                 client=cl)
                except Contract.DoesNotExist:
                    cl_ct = Contract(
                        contract_type=cts[0],
                        date_start=s_date, date_end=e_date,
                        date=cdate, client=cl, payer=cl,
                        payment_date=cdate,
                        number='O-%s' % data[2].strip(),
                        amount=cts[0].price,
                        manager=manager)
                    try:
                        cl_ct.save()
                        pass
                    except Exception, e:
                        print e
                    log_f.write(
                        'Contract add;%s;%s;%s\n' %
                        (cdate, cname, ' '.join(full_name))
                    )
            except Client.DoesNotExist:
                phone = data[13].strip()
                if len(phone) == 7:
                    phone = '499' + phone
                elif len(phone) == 10:
                    if int(phone[:3]) in [499, 495]:
                        phone = phone
                    elif int(phone[0]) == 9:
                        phone = '7' + phone
                    else:
                        log_f.write(
                            'error phone prefix "%s" in line #%d: %s\r' %
                            (int(phone[:3]), total, line)
                        )
                        continue
                elif len(phone) == 11:
                    try:
                        p = int(phone)
                    except Exception, e:
                        log_f.write(
                            'error phone "%s" in line #%d: %s\r' %
                            (phone, total, line)
                        )
                        continue
                    if int(phone[1]) == 9:
                        phone = '7' + phone[1:]
                log_f.write(
                    'New client;%s;%s;%s;%s\n' %
                    (born, ' '.join(full_name), cname, e_date)
                )
                cl = Client(first_name=full_name[1],
                            last_name=full_name[0],
                            patronymic=full_name[2],
                            born_date=born, phone=phone,
                            manager=manager)
                cl.save()
                cl_ct = Contract(contract_type=cts[0],
                                 date_start=s_date, date_end=e_date,
                                 date=cdate, client=cl, payer=cl,
                                 amount=cts[0].price,
                                 number='O-%s' % data[2].strip(),
                                 payment_date=cdate,
                                 manager=manager)
                try:
                    cl_ct.save()
                except Exception, e:
                    print e
                clntsave += 1
            except IndexError:
                log_f.write(
                    'Wrong patronymic;%s;%s;%s\n' %
                    (e_date, ' '.join(full_name), cname)
                )
        log_f.write('contract: %s ' % cname)
        log_f.write('full_name: %s\n' % ''.join(full_name))

f.close()
log_f.write('total read lines: %d\r\n' % total)
log_f.write('wrong data: %d\r\n' % wrong_data)
log_f.write('active contracts load: %d\r\n' % activecontracts)
log_f.write('Clients add: %d\r\n' % clntsave)
log_f.write('finish\r\n')
log_f.close()
