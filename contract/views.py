# -*- coding: utf-8 -*-
from datetime import datetime
from time import strptime
import json

from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from .forms import *
from .models import *
from person.models import Client
from person.forms import form_client_add
from finance.models import CreditsHistory, Goods
from finance.forms import FormCredits


day_name = "понедельник вторник среда четверг пятница суббота воскресенье"
day_name = day_name.split()
abc = settings.ABC


@login_required(login_url='/login/')
def date_start(request, id):
    """
    Update contract start date.
    """
    try:
        contract = Contract.objects.get(pk=int(id))
    except Contract.DoesNotExist:
        return HttpResponse('Не существующий договор',
                            mimetype='text/html; charset=utf-8')
    b_url = reverse('person_card', args=(contract.client.id, ))
    if request.method == 'POST':
        form = FormContractDateStart(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(b_url)
        else:
            errors = form.errors

    context_dict = dict(request=request, contract=contract, b_url=b_url)
    context_dict.update(csrf(request))
    return render_to_response('contract_date_start.html', context_dict)    


@login_required(login_url='/login/')
def card(request, id):
    try:
        contract = Contract.objects.get(pk=int(id))
    except Contract.DoesNotExist:
        return HttpResponse('Не существующий договор',
                            mimetype='text/html; charset=utf-8')
    b_url = reverse('person_card', args=(contract.client.id, ))

    if request.method == 'POST':
        if request.POST["card"]:
            contract.card = long(request.POST["card"])
            contract.save()
            return HttpResponseRedirect(b_url)

    context_dict = dict(request=request, contract=contract, b_url=b_url)
    context_dict.update(csrf(request))
    return render_to_response('contract_card.html', context_dict)


@login_required(login_url='/login/')
def exchange(request, c_id=0):
    """
    if exist active contract, then add new contract as is
    all dates without changes
    """
    try:
        contract = Contract.objects.get(pk=c_id)
    except Contract.DoesNotExist:
        return render_to_response("print_contracterr.html")
    err = 0
    form = form_client_add()
    if request.method == 'POST':
        clntid = int(request.POST['newclient'])
        if clntid > 0:
            try:
                clnt = Client.objects.get(pk=clntid)
            except Client.DoesNotExist:
                err = 'Ошибка при поиске клиента'
        else:
            post_values = request.POST.copy()
            post_values['manager'] = request.user.pk
            born = strptime(post_values['born_date'], "%d.%m.%Y")
            post_values['born_date'] = date(born.tm_year,
                                            born.tm_mon, born.tm_mday)
            form = form_client_add(post_values)
            if form.is_valid():
                try:
                    clnt = form.save()
                except Exception, e:
                    err = 'Ошибка сохранения нового клиента: ' + str(e)
            else:
                err = 'Ошибка данных нового клиента'
        if not err:
            contract.client = clnt
            if 'change_payer' in request.POST.keys():
                contract.payer = clnt
            contract.save()  # kwargs = {'exchange':1}
            url = reverse('p_active', args=(abc.index(clnt.last_name[0]), ))
            return HttpResponseRedirect(url)
    context_dict = dict(request=request, contract=contract,
                        err=err, form=form)
    context_dict.update(csrf(request))
    return render_to_response("contract_exchange.html", context_dict)


@login_required(login_url='/login/')
def contract_data(request, c_id=0):
    try:
        contract = Contract.objects.get(pk=c_id)
    except Contract.DoesNotExist:
        return render_to_response("print_contracterr.html")

    visits = Visits.objects.filter(contract=contract).order_by('date_start')
    freeze = Freeze.objects.filter(contract=contract).order_by('date_start')
    ch = CreditsHistory.objects.filter(contract=contract).order_by('date')
    context_dict = dict(visits=visits, freeze=freeze, ch=ch)
    return render_to_response("contract_data.html", context_dict)


@login_required(login_url='/login/')
def ban(request, cntr_id=0):
    res = "1"
    try:
        contract = Contract.objects.get(pk=cntr_id)
    except Contract.DoesNotExist:
        context_dict = dict(request=request, error=1, freeze=1,
                            msg='Активный договор не найден')
        return render_to_response("contractaction.html", context_dict)

    if request.method == 'POST':
        date_end = strptime(request.POST['date_end'], "%d.%m.%Y")
        date_end = date(date_end.tm_year, date_end.tm_mon, date_end.tm_mday, )
        res = contract.ban(date_end, request.POST['note'], request.user)
        url = reverse('person_card', args=(contract.client.pk, ))
        return HttpResponseRedirect(url)

    context_dict = dict(request=request, contract=contract, res=res)
    context_dict.update(csrf(request))
    return render_to_response("contract_ban.html", context_dict)


@login_required(login_url='/login/')
def bonus(request, cntr_id=0):
    res = "1"
    try:
        contract = Contract.objects.get(pk=cntr_id)
    except Contract.DoesNotExist:
        context_dict = dict(request=request, error=1, freeze=1,
                            msg='Активный договор не найден')
        return render_to_response("contractaction.html", context_dict)

    if request.method == 'POST':
        date_start = strptime(request.POST['date_start'], "%d.%m.%Y")
        date_start = date(date_start.tm_year,
                          date_start.tm_mon, date_start.tm_mday)
        res = contract.bonus(date_start, request.POST['days'],
                             request.POST['visits'], request.POST['note'],
                             request.user)
        url = reverse('pers_cont', args=(contract.client.pk, contract.pk))
        return HttpResponseRedirect(url)

    context_dict = dict(request=request, contract=contract, res=res)
    context_dict.update(csrf(request))
    return render_to_response("contract_bonus.html", context_dict)


@login_required(login_url='/login/')
def contract_freeze(request, cntr_id=0):
    res = "1"
    try:
        contract = Contract.objects.get(pk=cntr_id)
    except Contract.DoesNotExist:
        context_dict = dict(request=request, error=1, freeze=1,
                            msg='Активный договор не найден')
        return render_to_response("contractaction.html", context_dict)

    if request.method == 'POST':
        date_start = strptime(request.POST['date_start'], "%d.%m.%Y")
        date_start = date(date_start.tm_year,
                          date_start.tm_mon, date_start.tm_mday, )
        res = contract.freeze(date_start, request.POST['days'])

    freeze = Freeze.objects.filter(contract=contract).order_by('date_start')

    context_dict = dict(request=request, contract=contract,
                        freeze=freeze, res=res)
    context_dict.update(csrf(request))
    return render_to_response("contract_freeze.html", context_dict)


@login_required(login_url='/login/')
def contract_pay_freeze(request, cntr_id=0):
    res = "1"
    try:
        contract = Contract.objects.get(pk=cntr_id)
    except Contract.DoesNotExist:
        context_dict = dict(request=request, error=1, freeze=1,
                            msg='Активный договор не найден')
        return render_to_response("contractaction.html", context_dict)

    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['count'] = 1
        post_values['plan_date'] = datetime.now()
        post_values['amount'] = 0
        goods = Goods.objects.get(pk=int(post_values['goods']))
        post_values['department'] = goods.department
        post_values['contract'] = contract.pk
        post_values['payment_type'] = 1
        post_values['user'] = request.user.pk
        cf = FormCredits(post_values)
        if cf.is_valid():
            credit = cf.save()
            url = reverse('person_card', args=(contract.client.pk, ))
            return HttpResponseRedirect(url)
        else:
            return HttpResponse(cf.errors, mimetype="text/plain")
    freeze = Freeze.objects.filter(contract=contract).order_by('date_start')
    pay_freezes = Goods.objects.filter(is_pay_freeze=True)
    context_dict = dict(
        request=request, contract=contract, freeze=freeze, res=res,
        pay_freezes=pay_freezes)
    context_dict.update(csrf(request))
    return render_to_response("contract_pay_freeze.html", context_dict)


@login_required(login_url='/login/')
def visit_del(request, v_id):
    try:
        v = Visits.objects.get(pk=v_id)
        p = v.contract.client
        if v.is_online == -1:
            p.is_online = False
            p.save()
        err = 0
        v.delete()
    except Visits.DoesNotExist:
        err = 1
        p = ""

    context_dict = dict(request=request, err=err, p=p)
    return render_to_response("visit_del.html", context_dict)


@login_required(login_url='/login/')
def contract_type_edit(request, cntr_id=0, **kwargs):
    try:
        contractt = ContractType.objects.get(pk=cntr_id)
    except ContractType.DoesNotExist:
        context_dict = dict(request=request, error=1,
                            msg='Вид контракта не найден')
        return render_to_response("contractaction.html", context_dict)

    if request.method == 'POST':
        post_values = request.POST.copy()
        modified_by = request.user.id
        post_values['modified_by'] = modified_by
        post_values['version'] = contractt.version + 1
        date_start = strptime(post_values['date_start'], "%d.%m.%Y")
        post_values['date_start'] = datetime(date_start.tm_year,
                                             date_start.tm_mon,
                                             date_start.tm_mday)
        if post_values['date_start'].date() == datetime.now().date():
            contractt.is_active = False
            post_values['is_active'] = True
            contractt.save()
        else:
            post_values['is_active'] = False

        if post_values['name'] != contractt.name:
            ContractType.objects.filter(name=contractt.name).update(
                                                name=post_values['name'],
                                                modified_by=modified_by)

        if request.POST['group1'] == '1':
            post_values['max_visit'] = 99999

        if "is_child" in request.POST.keys():
            post_values['is_child'] = True
        else:
            post_values['is_child'] = False

        form = form_ContractType(post_values)
        if form.is_valid():
            form.save()
            url = reverse('ctype')
            return HttpResponseRedirect(url)
        else:
            return HttpResponse(form.errors, mimetype='text/html')

    if kwargs['act'] == 'hide':
        contractt.is_active = False
        msg = 'Вид контракта помечен как неактивный'
    elif kwargs['act'] == 'active':
        contractt.is_active = True
        msg = 'Вид контракта активирован'
    else:
        ptypes = PeriodTimeType.objects.filter(is_active=True).order_by('name')
        context_dict = dict(request=request, ct=contractt, ptypes=ptypes)
        context_dict.update(csrf(request))
        return render_to_response("type_edit.html", context_dict)

    contractt.save()
    context_dict = dict(request=request, msg=msg)
    return render_to_response("contractaction.html", context_dict)


@login_required(login_url='/login/')
def print_contract(request, id):
    try:
        text = ContractText.objects.latest('id')
    except ContractText.DoesNotExist:
        text = 0
    try:
        contract = Contract.objects.get(pk=id)
    except Contract.DoesNotExist:
        return render_to_response("print_contracterr.html")

    client = contract.payer
    if contract.contract_type.is_child:
        child = contract.client
    else:
        child = ""
    period_time_type = contract.contract_type.period_time_type.pk
    time = PeriodTime.objects.filter(period_time_type=period_time_type)
    if contract.payment_type == 1:
        payment = 'Безналичный'
    else:
        payment = 'Наличный'

    if contract.pay_plan:
        pplan = "в рассрочку"
        ppsteps = PayPlanSteps.objects.filter(pay_plan=contract.pay_plan).order_by('number')
    else:
        pplan = "Единовременно"
        ppsteps = PayPlanSteps.objects.filter(number=1)[:1]

    context_dict = dict(c=contract, p=client, t=time, pay=payment,
                        request=request, child=child,
                        pplan=pplan, ppsteps=ppsteps, text=text)
    return render_to_response("print_contract.html", context_dict)


@login_required(login_url='/login/')
def contract_menu(request, ):
    context_dict = dict(request=request, )
    return render_to_response("contract_menu.html", context_dict)


@login_required(login_url='/login/')
def pay_plan(request, **kwargs):
    if kwargs['act'] == 'add':
        if request.method == 'POST':
            errmsg = ''
            # check for sum of pay plan
            post_values = request.POST.copy()
            ppsumm = int(request.POST.get('amount'))
            ctype = ContractType.objects.filter(price=ppsumm)
            if len(ctype) > 0:
                post_values['plantype'] = 0
            else:
                if ppsumm == 100:
                    post_values['plantype'] = 1
                else:
                    errmsg = "Сумма должна быть равна 100% или\
                              одной из сумм видов договоров"
                    context_dict = dict(res=errmsg, request=request, )
                    context_dict.update(csrf(request))
                    return render_to_response("pay_plan_add.html",
                                              context_dict)

            if errmsg == "":
                # save pay plan
                form = form_PayPlan(post_values)
                if form.is_valid():
                    pay_plan = form.save()
                    i = 1
                    while "price" + str(i) in post_values.keys():
                        errmsg += ' ' + post_values['price' + str(i)]
                        ppsteps = PayPlanSteps()
                        ppsteps.pay_plan = pay_plan
                        ppsteps.amount = post_values['price' + str(i)]
                        ppsteps.number = i
                        ppsteps.save()
                        i += 1
                else:
                    errmsg = form.errors
            else:
                pass

        context_dict = dict(request=request)
        context_dict.update(csrf(request))
        return render_to_response("pay_plan_add.html", context_dict)

    lst = []
    pplans = PayPlan.objects.all().exclude(plantype=2)
    for pplan in pplans:
        pplansteps = PayPlanSteps.objects.filter(pay_plan=pplan)
        if pplan.plantype == 1:
            amount = "процентная рассрочка"
        else:
            amount = 0
            for steps in pplansteps:
                amount += steps.amount
            amount = 'на сумму ' + str(amount) + ' руб.'
        lst.append((pplan.pk, pplan.name, amount, pplansteps))
    context_dict = dict(lst=lst, request=request, )
    return render_to_response("contract_pay_plan.html", context_dict)


@login_required(login_url='/login/')
def contract_text(request, ):
    if request.method == 'POST':
        post_values = request.POST.copy()
        modified_by = request.user.id
        post_values['person'] = modified_by
        form = form_ContractText(post_values, request.FILES)
        if form.is_valid():
            form.save()
        context_dict = dict(request=request, )
        context_dict.update(csrf(request))
        return render_to_response("contract_text.html", context_dict)
    else:
        form = form_ContractText()
        context_dict = dict(form=form, request=request, )
        context_dict.update(csrf(request))
        return render_to_response("contract_text.html", context_dict)


@login_required(login_url='/login/')
def contract_period(request, **kwargs):
    if kwargs['act'] == 'add':
        if request.method == 'POST':
            ptype = PeriodTimeType()
            ptype.name = request.POST.get("name")
            ptype.save()
            for i in xrange(0, 7):
                if "wday" + str(i) in request.POST.keys():
                    visit_start = request.POST.get("starttime" + str(i))
                    visit_end = request.POST.get("endtime" + str(i))
                    model = PeriodTime()
                    model.period_time_type = ptype
                    model.period_visit_start = visit_start
                    model.period_visit_end = visit_end
                    model.period_visit_wday = i
                    model.save()

        context_dict = dict(week=day_name, request=request, )
        context_dict.update(csrf(request))
        return render_to_response("period_add.html", context_dict)

    ptypes = PeriodTimeType.objects.all()
    lst = []
    for ptype in ptypes:
        period = PeriodTime.objects.filter(period_time_type=ptype.pk)
        lst.append((ptype.pk, ptype.name, period))
    context_dict = dict(week=day_name, lst=lst, request=request, )
    return render_to_response("contract_period.html", context_dict)


@login_required(login_url='/login/')
def contract_type(request, **kwargs):
    if kwargs['act'] == 'add':
        form = form_ContractType()
        if request.method == 'POST':
            post_values = request.POST.copy()
            modified_by = request.user.id
            post_values['modified_by'] = modified_by
            if request.POST['group1'] == '1':
                post_values['max_visit'] = 99999

            post_values['version'] = 0
            post_values['date_start'] = datetime.today()
            if "is_child" in request.POST.keys():
                post_values['is_child'] = True
            else:
                post_values['is_child'] = False

            post_values['is_active'] = True

            form = form_ContractType(post_values)
            if form.is_valid():
                form.save()
                url = reverse('ctype')
                return HttpResponseRedirect(url)
            else:
                return HttpResponse(form.errors, mimetype='text/html')

        ptypes = PeriodTimeType.objects.all()
        context_dict = dict(form=form, ptypes=ptypes, request=request, )
        context_dict.update(csrf(request))
        return render_to_response("type_add.html", context_dict)

    if kwargs['act'] == 'all':
        # get list by last version for all contract types
        ctypes0 = ContractType.objects.filter(version=0).order_by('name')
        ctypes = []
        for t in ctypes0:
            ct = ContractType.objects.filter(name=t.name)\
                                     .order_by('-version')[0]
            history = ContractType.objects.filter(name=t.name)\
                                          .order_by('date_start')
            ctypes.append((ct.pk, ct.name, history))
        alltype = 1
    else:
        ctypes = ContractType.objects.filter(is_active=True).order_by('name')
        alltype = 0
    context_dict = dict(lst=ctypes, request=request, all=alltype)
    return render_to_response("contract_type.html", context_dict)


@login_required(login_url='/login/')
def contract_discount(request, **kwargs):
    if kwargs['act'] == 'del':
        cnt = 0
        if 'id' in request.GET.keys():
            try:
                d = Discount.objects.get(pk=int(request.GET['id']))
            except Exception, e:
                res = json.dumps(dict(res=-10))
                return HttpResponse(res, mimetype="application/json")
            try:
                d.delete()
                res = json.dumps(dict(res=1))
                return HttpResponse(res, mimetype="application/json")
            except Exception, e:
                res = json.dumps(dict(res=-100))
                return HttpResponse(res, mimetype="application/json")

    if kwargs['act'] == 'add':
        form = form_Discount()
        if request.method == 'POST':
            post_values = request.POST.copy()
            date_start = strptime(post_values['date_start'], "%d.%m.%Y")
            post_values['date_start'] = datetime(date_start.tm_year,
                                                 date_start.tm_mon,
                                                 date_start.tm_mday, )
            if "date_end" in post_values.keys()\
               and post_values['date_end'] != "":
                date_end = strptime(post_values['date_end'], "%d.%m.%Y")
                post_values['date_end'] = datetime(date_end.tm_year,
                                                   date_end.tm_mon,
                                                   date_end.tm_mday, )
            form = form_Discount(post_values)
            if form.is_valid():
                form.save()

        context_dict = dict(form=form, request=request, )
        context_dict.update(csrf(request))
        return render_to_response("discount_add.html", context_dict)

    discounts = Discount.objects.all()
    context_dict = dict(lst=discounts, request=request, )
    return render_to_response("contract_discount.html", context_dict)
