# -*- coding: utf-8 -*-
from time import strptime
from datetime import date, datetime, time, timedelta
from calendar import monthrange
from string import uppercase
from decimal import Decimal
import xlwt

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import F  # updated__gte=F('added_toSolr_date')

from finance.models import *
from contract.models import Visits
from core.models import User
from employees.models import (
    Visits as eVisits, Shift, Timetable, WorkRecord, Employee)
from reception.models import GuestVisits
from organizer.models import Guest as OGuest
from .models import *
from .forms import *
from .dbmodels import *
from .styles import *

report_top_prefix = settings.REPORT_TOP_PREFIX
pay_type = (u'нал.', u'без нал.', u'иное')


@login_required(login_url='/login')
def manager_sells(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)

    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=manager_sells.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("manager_sells")

    columns = []
    columns.append((u'Дата покупки', 4000))
    columns.append((u'ФИО ', 10000, ))
    columns.append((u'Наименование услуги', 6000))
    columns.append((u'Стоимость', 6000))
    columns.append((u'Скидка', 6000))
    columns.append((u'Внесенная сумма', 6000))
    head = u'Отчет по продажам менеджеров с: ' + s_date.strftime("%d.%m.%Y")
    head += u' по: ' + e_date.strftime("%d.%m.%Y")
    ws.write_merge(0, 0, 0, len(columns)-1, head, styleh)

    alignment = xlwt.Alignment()
    alignment.wrap = 1
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    styleth.alignment = alignment
    row_num = 1
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 35*20
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    manager = 0
    manager_name = ''
    total_man = 0
    total = 0
    for ch in ManagerSells.objects.filter(
            date__range=(s_date, e_date), selltype__gt=0, firstptt=1
    ).order_by('manager', 'date'):
        row_num += 1
        total_man += ch.amount
        total += ch.amount
        if manager != ch.manager.pk:
            if manager > 0:
                ws.write_merge(
                    row_num, row_num, 0, len(columns)-1,
                    u'Итого по ' + manager_name + ': ' + str(total_man),
                    styleth)
                total_man = 0
                row_num += 1
            manager = ch.manager.pk
            manager_name = ch.manager.initialsC()
            ws.write_merge(
                row_num, row_num, 0, len(columns)-1,
                u'Продавец: ' + manager_name, styleth)
            row_num += 1

        if ch.selltype == 1:
            # Contract data
            client = ch.contract.client.initialsC()
            if ch.contract.date_joined.date() == ch.date.date():
                goodsname = ch.contract.contract_type.name
            else:
                goodsname = ch.contract.contract_type.name + u' доплата'
            price = ch.contract.amount
            if ch.contract.discount:
                discount = ch.contract.discount.value
            else:
                discount = None
        else:
            client = ch.client.initialsC()
            goodsname = ch.goods.name
            price = ch.goods.priceondate(ch.date)
            discount = None

        ws.write(row_num, 0, ch.date.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 1, client, style)
        ws.write(row_num, 2, goodsname, style)
        ws.write(row_num, 3, price, style)
        ws.write(row_num, 4, discount, style)
        ws.write(row_num, 5, ch.amount, style)

    row_num += 1
    ws.write_merge(
        row_num, row_num, 0, len(columns)-1,
        u'Итого по ' + manager_name + ': ' + str(total_man), styleth)
    row_num += 1
    ws.write_merge(
        row_num, row_num, 0, len(columns)-1, u'Итого по всем: ' + str(total),
        styleth)
    wb.save(response)
    return response


@login_required(login_url='/login')
def contract_end(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)

    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=contract_end.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("contract_end")

    columns = []
    columns.append((u'ФИО ', 10000, ))
    columns.append((u'Телефон', 6000))
    columns.append((u'Вид контракта', 6000))
    columns.append((u'Дата покупки', 4000))
    columns.append((u'Номер контракта', 4000))
    columns.append((u'Дата начала', 4000))
    columns.append((u'Дата окончания', 4000))
    columns.append((u'ФИО менеджера', 8000))
    columns.append((u'Активный', 4000))

    head = u'Отчет об окончании контракта с: ' + s_date.strftime("%d.%m.%Y")
    head += u' по: ' + e_date.strftime("%d.%m.%Y")
    ws.write_merge(0, 0, 0, len(columns)-1, head, styleh)

    alignment = xlwt.Alignment()
    alignment.wrap = 1
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    styleth.alignment = alignment
    row_num = 1
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 35*20
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    s_date = s_date + timedelta(days=1)
    e_date = e_date + timedelta(days=1)
    client_has_new = Contract.objects.filter(is_current=2).values('client')
    contracts = Contract.objects.select_related('client')
    contracts_end = contracts.filter(
        date_end__gte=s_date, date_end__lte=e_date).exclude(is_current=3)
    exclude_prlongation = contracts_end.exclude(client__in=client_has_new)
    clients = []
    for c in exclude_prlongation.order_by('client__manager', 'date_end'):
        if c.client in clients:
            continue
        clients.append(c.client)
        row_num += 1
        is_active = 'да' if c.client.is_active else 'нет'
        date_end = (c.date_end - timedelta(days=1)).strftime("%d.%m.%Y")
        ws.write(row_num, 0, c.client.initialsC(), style)
        ws.write(row_num, 1, c.client.phone, style)
        ws.write(row_num, 2, c.contract_type.name, style)
        ws.write(row_num, 3, c.date_joined.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 4, c.number, style)
        ws.write(row_num, 5, c.date_start.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 6, date_end, styled)
        ws.write(row_num, 7, c.client.manager.initialsC(), style)
        ws.write(row_num, 8, is_active, style)

    wb.save(response)
    return response


@login_required(login_url='/login')
def trainer_ptt(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)
    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=trainer_ptt.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("trainer_ptt", cell_overwrite_ok=True)
    head_data = s_date.strftime("%d.%m.%Y"), e_date.strftime("%d.%m.%Y")
    head = u'Статистика по тренерам с %s по %s' % head_data
    columns = []
    columns.append((u'Наименование услуги', 6000))
    columns.append((u'Дата продажи', 8000))
    columns.append((u'Стоимость', 6000))

    row_num = 0
    ws.write_merge(row_num, 0, 0, len(columns)-1, head, styleh)

    row_num = 1
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    ch = CreditsHistory.objects.filter(
        date__range=(s_date, e_date), employee__isnull=False
    ).values('employee')

    alignment = xlwt.Alignment()
    alignment.wrap = 1
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    styleth.alignment = alignment

    for t in Employee.objects.filter(
            pk__in=ch).order_by('lastname', 'firstname'):
        row_num += 1
        fname = t.lastname.title(), t.firstname.title(), t.patronymic.title()
        fullname = u'Тренер: %s %s %s' % fname
        ws.write_merge(row_num, row_num, 0, len(columns)-1, fullname, styleth)
        total = 0
        for cr in CreditsHistory.objects.filter(
                date__range=(s_date, e_date), employee=t):
            row_num += 1
            total += cr.amount
            ws.write(row_num, 0, cr.goods.name, style)
            ws.write(row_num, 1, cr.date.strftime("%d.%m.%Y"), styled)
            ws.write(row_num, 2, cr.amount, stylef)
        row_num += 1
        total_str = u'Итого по %s:' % (t.initials(),)
        ws.write(row_num, 0, total_str, styleth)
        # ws.write(row_num, 1, )
        ws.write_merge(row_num, row_num, 1, len(columns)-1, total, stylethf)

    wb.save(response)
    return response


@login_required(login_url='/login')
def employees(request, ):
    d = datetime.now()
    month = int(d.month)
    year = int(d.year)
    day = int(d.day)
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=employees.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("employees", cell_overwrite_ok=True)
    head_data = day, month_name_ru(month), year
    head = u'Список сотрудников по состоянию на: %s/%s/%s' % head_data
    columns = []
    columns.append((u'№', 2000))
    columns.append((u'ФИО', 8000))
    columns.append((u'Должность', 6000))
    columns.append((u'Телефон', 6000))

    row_num = 0
    ws.write_merge(row_num, 0, 0, len(columns)-1, head, styleh)

    alignment = xlwt.Alignment()
    alignment.wrap = 1
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    styleth.alignment = alignment
    row_num = 1
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    wr = WorkRecord.objects.filter(date_end__isnull=True).values('employee')
    row_cnt = 0
    for e in Employee.objects.filter(pk__in=wr).order_by('lastname'):
        row_num += 1
        row_cnt += 1
        fname = e.lastname.title(), e.firstname.title(), e.patronymic.title()
        fullname = '%s %s %s' % fname
        position = e.currwork().wposition.position.name
        ws.write(row_num, 0, row_cnt, style)
        ws.write(row_num, 1, fullname, style)
        ws.write(row_num, 2, position, style)
        ws.write(row_num, 3, e.phone, style)

    wb.save(response)
    return response


@login_required(login_url='/login')
def debtors_menu(request, ):
    m_list = User.objects.filter(groups__name='manager')  # manual create
    context_dict = dict(request=request, m_list=m_list)
    return render_to_response('r_debtors.html', context_dict)


@login_required(login_url='/login')
def debtors(request, manager, ):
    manager = User.objects.filter(groups__name='manager', id=int(manager))
    if manager.count() != 1:
        return HttpResponse(u'Not exist manager', mimetype='text/html')
    else:
        manager = manager[0]
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("debtors", cell_overwrite_ok=True)
    head = u'отчет по должникам по рассрочкам \n'
    head += u'Менеджер: ' + manager.initials()

    columns = []
    columns.append((u'ФИО клиента', 8000))
    columns.append((u'Телефон', 6000))
    columns.append((u'Номер контракта', 4000))
    columns.append((u'Вид контракта', 6000))
    columns.append((u'Дата покупки', 4000))
    columns.append((u'Дата окончания', 4000))
    columns.append((u'Схема рассрочки', 6000))
    columns.append((u'Стоимость (с учетом скидки)', 5000))
    columns.append((u'Сумма оплаты', 4000))
    columns.append((u'Сумма задолжности на текущий момент', 5000))
    columns.append((u'Остаток задолжности', 5000))

    row_num = 0
    ws.write_merge(row_num, 0, 0, len(columns)-1, head, styleh)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 25*20

    alignment = xlwt.Alignment()
    alignment.wrap = 1
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    styleth.alignment = alignment
    row_num = 1
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 35*20
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    row_num = 2
    clients = Client.objects.filter(manager=manager)
    # contracts = Contract.objects.filter(client__in=clients)
    contracts = Credits.objects.filter(
        contract__isnull=False, plan_date__lte=datetime.now()
    ).values('contract')
    for c in Contract.objects.filter(client__in=clients, pk__in=contracts, ):
        # for cr in Credits.objects.filter(contract__in=contracts):
        ws.write(row_num, 0, c.client.initialsC(), style)
        ws.write(row_num, 1, c.client.phone, style)
        ws.write(row_num, 2, c.number, style)
        ws.write(row_num, 3, c.contract_type.name, style)
        ws.write(row_num, 4, c.date_joined.strftime("%d.%m.%Y"), styledt)
        ws.write(row_num, 5, c.date_end.strftime("%d.%m.%Y"), styledt)
        if c.pay_plan:
            if c.pay_plan.plantype < 2:
                ws.write(row_num, 6, c.pay_plan.name, style)
            else:
                ws.write(row_num, 6, u'индивидуальная', style)
        else:
            ws.write(row_num, 6, '', style)
        ws.write(row_num, 7, c.amount, stylef)
        # the payments has done
        payments = CreditsHistory.objects.filter(
            contract=c).aggregate(Sum('amount'))
        if payments['amount__sum']:
            payments = payments['amount__sum']
        else:
            payments = 0
        ws.write(row_num, 8, payments, stylef)
        # the credits sum
        credits = Credits.objects.filter(
            contract=c, plan_date__lte=datetime.now()
        ).aggregate(Sum('amount'))
        credits = credits['amount__sum']
        ws.write(row_num, 9, credits, stylef)
        last_credits = Credits.objects.filter(
            contract=c, plan_date__gte=datetime.now()
        ).aggregate(Sum('amount'))
        last_credits = last_credits['amount__sum']
        ws.write(row_num, 10, last_credits, stylef)
        row_num += 1

    wb.save(response)
    return response


@login_required(login_url='/login')
def manager(request, year, month):
    year = int(year)
    month = int(month)
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("manager", cell_overwrite_ok=True)
    head = u'отчет менеджера за: ' + month_name_ru(month) + ' '
    head += str(year) + u'года'

    columns = []
    columns.append((u'дата ', 4000))
    columns.append((u'Номер контракта', 4000))
    columns.append((u'Вид контракта', 6000))
    columns.append((u'Скидка', 4000))
    columns.append((u'Продление / впервые', 4000))
    columns.append((u'Номер карты', 6000))
    columns.append((u'ФИО клиента', 8000))
    columns.append((u'Оплата: полная / рассрочка', 3000))
    columns.append((u'Вид оплаты', 4000))
    columns.append((u'Стоимость', 4000))
    columns.append((u'Взнос', 4000))
    columns.append((u'Доплата', 4000))
    columns.append((u'Фактическая оплата', 8000))
    columns.append((u'ФИО менеджера', 8000))
    columns.append((u'Итого за день', 6000))
    columns.append((u'ФИО продовца', 8000))

    row_num = 0
    ws.write_merge(row_num, 0, 0, len(columns)-1, head, styleh)

    alignment = xlwt.Alignment()
    alignment.wrap = 1
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    styleth.alignment = alignment
    row_num = 1
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 35*20
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    first_text = (u'Повторно', u'Впервые', u'')
    day_summ = 0
    mdays = monthrange(year, month)[1]
    for d in xrange(mdays):
        day = d + 1
        d = date(year, month, day)
        if day_summ > 0:
            ws.write(row_num, 14, day_summ, style)
        day_summ = 0
        for cr in CreditsHistory.objects.filter(
                date__month=month, date__year=year, date__day=day,):
            if cr.contract:
                c = cr.contract
                row_num += 1
                if c.date_joined.date() == d:
                    contribution = cr.amount
                    e_pay = ''
                    if c.is_first():
                        first = 1
                    else:
                        first = 0
                else:
                    contribution = ''
                    e_pay = cr.amount
                    first = 2

                if c.pay_plan:
                    pplan = u'Рассрочка'
                else:
                    pplan = u'Полная'
                ws.write(row_num, 1, c.number, style)
                ws.write(row_num, 2, c.contract_type.name, style)
                ws.write(row_num, 4, first_text[first], style)
                ws.write(row_num, 5, c.card, style)
                ws.write(row_num, 6, c.client.initialsC(), style)
                ws.write(row_num, 7, pplan, style)
                ws.write(row_num, 9, c.contract_type.price, style)
                ws.write(row_num, 10, contribution, style)
                ws.write(row_num, 11, e_pay, style)
                ws.write(row_num, 12, cr.amount, style)
                ws.write(row_num, 13, c.client.manager.initials(), style)
                if cr.contract.discount:
                    ws.write(row_num, 3, c.discount.value, style)
                else:
                    ws.write(row_num, 3, '', style)
                day_summ += cr.amount
            elif cr.goods:
                ptt_line = 0
                if cr.goods.goods_type.name == 'PTT':
                    row_num += 1
                    ptts = Client_PTT.objects.filter(
                        date__month=month, date__year=year, date__day=day,
                        employee=cr.employee, goods=cr.goods, client=cr.client
                    ).order_by('date')
                    if ptts.count() > 1:
                        ptt = ptts[ptt_line]
                        ptt_line += 1
                    else:
                        ptt_line = 0
                        ptt = ptts[0]

                    ws.write(row_num, 1, ptt.number(), style)
                    ws.write(row_num, 2, cr.goods.name, style)
                    ws.write(row_num, 3, '', style)
                    ws.write(row_num, 4, first_text[ptt.is_first()], style)
                    ws.write(row_num, 5, ptt.number(), style)
                    ws.write(row_num, 6, ptt.client.initialsC(), style)
                    ws.write(row_num, 7, '', style)
                    ws.write(row_num, 9, cr.goods.priceondate(d), style)
                    ws.write(row_num, 10, cr.amount, style)
                    ws.write(row_num, 11, '', style)
                    ws.write(row_num, 12, cr.amount, style)
                    ws.write(row_num, 13, ptt.client.manager.initials(), style)
                    day_summ += cr.amount
                else:
                    continue
            else:
                continue
            ws.write(row_num, 0, d, styled)
            ws.write(row_num, 8, pay_type[cr.payment_type], style)
            ws.write(row_num, 14, '', style)
            ws.write(row_num, 15, cr.user.initials(), style)

    wb.save(response)
    return response


@login_required(login_url='/login')
def ptt(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)

    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("ptt")

    head = u'Персональные тренировки за период c: '\
        + s_date.strftime("%d.%m.%Y")
    head += u' по: ' + e_date.strftime("%d.%m.%Y")
    ws.write_merge(0, 0, 0, 10, head, styleh)

    row_num = 1
    columns = []
    columns.append((u'Номер карты ', 4000))
    columns.append((u'Дата продажи', 6000))
    columns.append((u'Вид блока', 6000))
    columns.append((u'Стоимость, руб.', 5000))
    columns.append((u'Вид оплаты', 4000))
    columns.append((u'Впервые / Повторно', 5000))
    columns.append((u'ФИО ', 8000))
    columns.append((u'Тренер ', 8000))
    columns.append((u'Менеджер ', 8000))
    columns.append((u'Продавец', 8000))
    columns.append((u'Карта выдана ', 4000, 0))

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    lst = Client_PTT.objects.filter(
        date__range=(s_date, e_date)).order_by('date')

    ptt_first = (u'Повторно', u'Впервые')

    for ptt in lst:
        row_num += 1
        fullname = ptt.client.initialsC()
        trainer = ptt.employee.initials()
        manager = ptt.client.manager.initials()
        seller = ptt.user.initials()
        if not ptt.is_card:
            url = reverse('ptt_card', args=(ptt.pk, ))
            url = request.build_absolute_uri(url)
            link = u'HYPERLINK("' + url + u'"; "Не выдана")'
            is_card = xlwt.Formula(link)
            st = style_red
        else:
            is_card = u'Выдана'
            st = style
        ws.write(row_num, 0, str(ptt.number()), style)
        ws.write(row_num, 1, ptt.date.strftime("%d.%m.%Y %H:%M"), styledt)
        ws.write(row_num, 2, ptt.goods.name, style)
        ws.write(row_num, 3, ptt.goods.priceondate(ptt.date), stylef)
        ws.write(row_num, 4, pay_type[ptt.payment_type], style)
        ws.write(row_num, 5, ptt_first[ptt.is_first()], style)
        ws.write(row_num, 6, fullname, style)
        ws.write(row_num, 7, trainer, style)
        ws.write(row_num, 8, manager, style)
        ws.write(row_num, 9, seller, style)
        ws.write(row_num, 10, is_card, st)

    wb.save(response)
    return response


@login_required(login_url='/login')
def e_visits(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)

    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    ldate = Shift.objects.all().aggregate(Max('date'))
    shifts = Shift.objects.filter(date=ldate['date__max'])
    ttable = Timetable.objects.filter(
        date__range=(s_date, e_date), shift__in=shifts)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("e_visits")

    head = u'Посещения клуба за период c: ' + s_date.strftime("%d.%m.%Y")
    head += u' по: ' + e_date.strftime("%d.%m.%Y")

    row_num = 1
    columns = []
    columns.append((u'дата ', 4000))
    columns.append((u'день недели ', 4000))
    columns.append((u'ФИО ', 8000))
    columns.append((u'Время прихода ', 4000))
    columns.append((u'Время ухода ', 4000))

    ws.write_merge(0, 0, 0, len(columns)-1, head, styleh)

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    lst = eVisits.objects.filter(
        date_start__gte=s_date, date_start__lte=e_date).order_by('date_start')
    for v in lst:
        row_num += 1
        fullname = v.employee.initials()
        try:
            Timetable.objects.get(
                date=v.date_start.date(), employee=v.employee)
            nstyle = style_red
        except Timetable.DoesNotExist:
            nstyle = style
        ws.write(row_num, 0, v.date_start.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 1, week_days_ru(v.date_start.weekday()), nstyle)
        ws.write(row_num, 2, fullname, nstyle)
        ws.write(row_num, 3, v.date_start.strftime("%H:%M"), stylet)
        if v.date_end:
            data = v.date_end.strftime("%H:%M")
        else:
            data = ''
        ws.write(row_num, 4, data, stylet)

    wb.save(response)
    return response


@login_required(login_url='/login')
def reception_visits(request, ):
    Y = datetime.today().year
    m = datetime.today().strftime("%m")
    d = datetime.today().strftime("%d")
    context_dict = dict(request=request, Y=Y, m=m, d=d)
    return render_to_response('reception_visits.html', context_dict)


@login_required(login_url='/login')
def organizer(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)

    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("visits")

    columns = []
    columns.append((u'Номер', 2000, ))
    columns.append((u'ФИО ', 8000, ))
    columns.append((u'Телефон', 4000, ))
    columns.append((u'Гость/звонок', 6000, ))
    columns.append((u'Дата занесения в органайзер', 8000, ))
    columns.append((u'Абонемент куплен да/нет', 8000, ))
    columns.append((u'Коментарий', 4000, ))
    columns.append((u'Менеджер', 8000, ))

    head = u'Выгрузка органайзера в exel'
    ws.write_merge(0, 0, 0, len(columns)-1, head, styleh)
    row_num = 1
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    row_num = 1
    guests = OGuest.objects.filter(
        date__range=(s_date, e_date)).order_by('date')
    for i, g in enumerate(guests):
        row_num += 1
        ws.write(row_num, 0, i, style)
        ws.write(row_num, 1, g.fullname(), style)
        ws.write(row_num, 2, g.phone, style)
        ws.write(row_num, 3, g.gtype_str(), style)
        ws.write(row_num, 4, g.date.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 5, g.is_client_str(), style)
        ws.write(row_num, 6, g.note, style)
        ws.write(row_num, 7, g.manager.initialsC(), style)
    wb.save(response)
    return response


@login_required(login_url='/login')
def organizer_full(request):
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("visits")

    columns = []
    columns.append((u'Номер п/п', 2000, ))
    columns.append((u'ФИО ', 8000, ))
    columns.append((u'Телефон', 4000, ))
    columns.append((u'Гость/звонок', 6000, ))
    columns.append((u'Дата занесения в органайзер', 8000, ))
    columns.append((u'Абонемент куплен да/нет', 8000, ))
    columns.append((u'Коментарий', 4000, ))
    columns.append((u'Менеджер', 8000, ))

    head = u'Выгрузка органайзера в exel'
    ws.write_merge(0, 0, 0, len(columns)-1, head, styleh)
    row_num = 1
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    row_num = 1
    guests = OGuest.objects.all().order_by('date')
    for i, g in enumerate(guests):
        row_num += 1
        ws.write(row_num, 0, i, style)
        ws.write(row_num, 1, g.fullname(), style)
        ws.write(row_num, 2, g.phone, style)
        ws.write(row_num, 3, g.gtype_str(), style)
        ws.write(row_num, 4, g.date.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 5, g.is_client_str(), style)
        ws.write(row_num, 6, g.note, style)
        ws.write(row_num, 7, g.manager.initialsC(), style)
    wb.save(response)
    return response


@login_required(login_url='/login')
def visits(request, syear, smonth, sday, eyear, emonth, eday):
    syear = int(syear)
    smonth = int(smonth)
    sday = int(sday)
    eyear = int(eyear)
    emonth = int(emonth)
    eday = int(eday)

    s_date = datetime.combine(date(syear, smonth, sday), time.min)
    e_date = datetime.combine(date(eyear, emonth, eday), time.max)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("visits")

    columns = []
    columns.append((u'дата ', 4000, ))
    columns.append((u'ФИО ', 8000, ))
    columns.append((u'Время прихода ', 4000, ))
    columns.append((u'Время ухода ', 4000, ))
    columns.append((u'Шкафчик # ', 3000, ))

    head = u'Посещения клуба за период c: ' + s_date.strftime("%d.%m.%Y")
    head += u' по: ' + e_date.strftime("%d.%m.%Y")
    ws.write_merge(0, 0, 0, len(columns)-1, head, styleh)

    row_num = 1
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    lst = Visits.objects.filter(date_start__gte=s_date,
                                date_end__lte=e_date).order_by('date_start')
    for v in lst:
        row_num += 1
        fullname = v.contract.client.initialsC()
        ws.write(row_num, 0, v.date_start.strftime("%d.%m.%Y"), styled)
        ws.write(row_num, 1, fullname, style)
        ws.write(row_num, 2, v.date_start.strftime("%H:%M"), stylet)
        ws.write(row_num, 3, v.date_end.strftime("%H:%M"), stylet)
        ws.write(row_num, 4, v.locker, style)

    wb.save(response)
    return response


@login_required(login_url='/login')
def sells(request, year, month, other):
    month = int(month)
    year = int(year)
    other = int(other)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("sells")

    ch_dep = CreditsHistory.objects.filter(
        date__month=month, date__year=year,).values('department')
    need_dp = DepartmentsNames.objects.filter(
        department__in=ch_dep).values_list('pk', flat=True)
    columns = []
    columns.append((u'Дата ', 4000, 0))
    for dn in DepartmentsNames.list():
        if dn not in need_dp:
            continue
        if DepartmentsNames.list()[dn]:
            columns.append((DepartmentsNames.list()[dn], 4000, dn))
        else:
            columns.append((u'Отдел ' + str(dn), 4000, dn))

    columns.append((u'Сумма ', 4000, 9999))

    row_num = 0
    head = month_name_ru(month) + '   ' + str(year)
    col_join = len(columns) - 4
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 15*20
    if col_join < 1:
        col_join = 1
    ws.write_merge(row_num, 0, 0, col_join, head, styleh)
    ws.write_merge(
        row_num, 0, col_join + 1, col_join + 3, report_top_prefix, styleph)
    row_num = 1
    last_col = len(columns) - 1
    for col_num in xrange(len(columns)):
        if col_num == 0:
            ws.write_merge(row_num, 2, 0, 0, columns[col_num][0], styleth)
        elif col_num == last_col:
            ws.write_merge(
                row_num, 2, last_col, last_col, columns[col_num][0], styleth)
        else:
            ws.write(row_num, col_num, columns[col_num][0], styleth)
            ws.write(
                row_num + 1, col_num,
                u'Отдел ' + str(columns[col_num][2]), styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    row_num = 2
    total_summ = 0
    mdays = monthrange(year, month)[1]
    for d in xrange(mdays):
        row_num += 1
        day = d + 1
        day_summ = 0
        for col_num in xrange(len(columns)):
            if col_num == 0:
                data = date(year, month, day).strftime("%d.%m.%Y")
                st = stylethd
            elif columns[col_num][2] == 9999:
                st = styleth
                sl = col_idx2str(1)
                el = col_idx2str(col_num-1)
                formula = 'SUM(' + sl + str(row_num + 1) + ':'\
                                 + el + str(row_num + 1) + ')'
                data = xlwt.Formula(formula)
            else:
                st = style
                department = columns[col_num][2]  # cash section
                if other:
                    dep_summ = CreditsHistory.objects.filter(
                        date__month=month, date__year=year, date__day=day,
                        department=department, is_return=0,
                    ).aggregate(Sum('amount'))
                else:
                    dep_summ = CreditsHistory.objects.filter(
                        date__month=month, date__year=year, date__day=day,
                        department=department, is_return=0,
                    ).exclude(
                        payment_type=2).aggregate(Sum('amount'))
                data = dep_summ['amount__sum']
                if data:
                    day_summ += data
            ws.write(row_num, col_num, data, st)

    row_num += 1
    ws.write(row_num, 0, 'Итого:', styleth)
    for col_num in xrange(1, len(columns)):
        l = col_idx2str(col_num)
        formula = 'SUM(' + l + '4:' + l + str(mdays+3) + ')'
        ws.write(row_num, col_num, xlwt.Formula(formula), styleth)
    wb.save(response)
    return response


@login_required(login_url='/login')
def menu(request, ):
    Y = datetime.today().year
    m = datetime.today().strftime("%m")
    d = datetime.today().strftime("%d")

    context_dict = dict(request=request, Y=Y, m=m, d=d,)
    return render_to_response('reports_menu.html', context_dict)


@login_required(login_url='/login')
def departments_names(request, ):
    if request.method == 'POST':
        i = 0
        form_val = dict()
        for n in request.POST.getlist('name'):
            i += 1
            form_val['department'] = i
            form_val['name'] = n
            try:
                inst = DepartmentsNames.objects.get(pk=i)
                form = FormDepartmentsNames(form_val, instance=inst)
            except DepartmentsNames.DoesNotExist:
                form = FormDepartmentsNames(form_val)
            if form.is_valid():
                form.save()
            else:
                return HttpResponse(form.errors, mimetype="text/plain")
        return HttpResponseRedirect(reverse('reports_menu'))
    lst = DepartmentsNames.list()
    context_dict = dict(request=request, lst=lst)
    context_dict.update(csrf(request))
    return render_to_response('departments_names.html', context_dict)


@login_required(login_url='/login')
def reception_day(request, year, month, day,):
    title = u'Отчет рецепциониста'
    month = int(month)
    year = int(year)
    day = int(day)
    td = date(year, month, day)
    b_date = datetime.combine(td, time.min)
    e_date = datetime.combine(td, time.max)
    lst = CreditsHistory.objects.filter(
        date__range=(b_date, e_date)).exclude(payment_type=2).values('check')

    cclst = CashCheck.objects.filter(pk__in=lst).order_by('date')

    total = CreditsHistory.objects.filter(
        date__range=(b_date, e_date), is_return=0).exclude(
        payment_type=2).aggregate(Sum('amount'))['amount__sum']
    dtotal = []
    for d in settings.DEPARTMENTS:
        dsumm = 0
        cash = CreditsHistory.objects.filter(
            department=d, payment_type=0, date__range=(b_date, e_date),
            is_return=0).aggregate(Sum('amount'))['amount__sum']
        if cash:
            dsumm += cash

        cashless = CreditsHistory.objects.filter(
            department=d, payment_type=1, date__range=(b_date, e_date),
            is_return=0, ).aggregate(Sum('amount'))['amount__sum']
        if cashless:
            dsumm += cashless

        dtotal.append((d, dsumm, cash, cashless))

    Y = td.year
    m = td.strftime("%m")
    d = td.strftime("%d")
    context_dict = dict(
        request=request, lst=cclst, title=title, total=total,
        dtotal=dtotal, cashhost=settings.CASHIER_HOST, Y=Y, m=m, d=d)
    response = render_to_response('reception_day.html', context_dict)

    return response


@login_required(login_url='/login')
def reception(request, year, month, day, other, ):
    day = int(day)
    month = int(month)
    year = int(year)
    other = int(other)
    td = date(year, month, day)

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("receprion")

    head = u'Отчет рецепциониста за: %s' % td.strftime("%d.%m.%Y")
    columns = []
    columns.append((u'Время', 6000))
    columns.append((u'Клиент', 8000))
    columns.append((u'Товар', 6000))
    columns.append((u'Количество', 6000))
    columns.append((u'Цена', 6000))
    columns.append((u'Сумма', 6000))
    columns.append((u'Вид оплаты', 6000))

    row_num = 0
    ws.write_merge(row_num, 0, 0, len(columns)-1, head, styleh)

    row_num = 1
    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], styleth)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    b_date = datetime.combine(td, time.min)
    e_date = datetime.combine(td, time.max)
    if other:
        payments = CreditsHistory.objects.filter(
            date__range=(b_date, e_date)).order_by('date')
    else:
        payments = CreditsHistory.objects.filter(
            date__range=(b_date, e_date)).exclude(
            payment_type=2).order_by('date')
    for ch in payments:
        row_num += 1
        ws.write(row_num, 0, ch.date.strftime("%H:%M"), stylet)
        ws.write(row_num, 1, ch.username(), style)
        ws.write(row_num, 2, ch.goodsname(), style)
        ws.write(row_num, 3, ch.count, style)

        ws.write(row_num, 4, ch.goodsprice(), stylef)
        ws.write(row_num, 5, ch.amount, style)

        if ch.payment_type == 1:
            str_paytype = u'безнал'
        elif ch.payment_type == 2:
            str_paytype = u'иное'
        else:
            str_paytype = u'наличными'

        ws.write(row_num, 6, str_paytype, style)

    if other:
        total = CreditsHistory.objects.filter(
            date__range=(b_date, e_date)).aggregate(
            Sum('amount'))['amount__sum']
    else:
        total = CreditsHistory.objects.filter(
            date__range=(b_date, e_date)).exclude(
            payment_type=2).aggregate(Sum('amount'))['amount__sum']

    row_num += 1
    ws.write(row_num, 0, 'Итого:', styleh)
    ws.write(row_num, 1, total, stylethf)
    # add the line before details
    row_num += 1

    dsumm = 0
    for d in settings.DEPARTMENTS:
        # if the previous department has sells, miss one line
        if dsumm > 0:
            row_num += 1
        dsumm = 0
        cash = CreditsHistory.objects.filter(
            department=d, payment_type=0, date__range=(b_date, e_date)
        ).aggregate(Sum('amount'))['amount__sum']
        if cash:
            dsumm += cash

        cashless = CreditsHistory.objects.filter(
            department=d, payment_type=1, date__range=(b_date, e_date)
        ).aggregate(Sum('amount'))['amount__sum']
        if cashless:
            dsumm += cashless

        if other:
            other_summ = CreditsHistory.objects.filter(
                department=d, payment_type=2, date__range=(b_date, e_date)
            ).aggregate(Sum('amount'))['amount__sum']
            if other_summ:
                dsumm += other_summ
        else:
            other_summ = 0

        if dsumm > 0:
            row_num += 1
            d_str = 'отдел №%s' % d
            ws.write(row_num, 0, d_str, styleh)
            ws.write(row_num, 1, dsumm, stylethf)
        if cash > 0:
            row_num += 1
            ws.write(row_num, 0, 'наличными:', styleh)
            ws.write(row_num, 1, cash, stylethf)
        if cashless > 0:
            row_num += 1
            ws.write(row_num, 0, 'безнал:', styleh)
            ws.write(row_num, 1, cashless, stylethf)
        if other_summ > 0:
            row_num += 1
            ws.write(row_num, 0, 'иное:', styleh)
            ws.write(row_num, 1, other_summ, stylethf)
    wb.save(response)
    return response


def month_name_ru(idx):
    month_name = (
        u'', u'Январь', u'Февраль', u''
        u'Март', u'Апрель', u'Май',
        u'Июнь', u'Июль', u'Август',
        u'Сентябрь', u'Октябрь', u'Ноябрь',
        u'Декабрь')
    return month_name[idx]


def week_days_ru(idx):
    week_days = (u'Понедельник', u'Вторник', u'Среда', u'Четверг',
                 u'Пятница', u'Суббота', u'Воскресенье')
    return week_days[idx]


def col_idx2str(idx):
    idx += 1
    col = ''
    while (idx > 0):
        mod = (idx - 1) % 26
        col = uppercase[mod] + col
        idx = (idx - mod) / 26
    return col
