# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta, date
from time import strptime, time

from django.core.context_processors import csrf
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from forms import *
from models import *
from contract.forms import form_Contract
from contract.models import *
from finance.models import *
from finance.forms import FormClient_PTT, FormCredits
from organizer.models import Guest
from reception.models import Guest as rGuest
from core.models import User


abc = settings.ABC


@login_required(login_url='/login')
def person_edit(request, clnt_id=0, ):
    try:
        clnt = Client.objects.get(pk=clnt_id)
    except Client.DoesNotExist:
        context_dict = dict(b_url=reverse('p_active', args=(0, )))
        return render_to_response("clienterr.html", context_dict)

    if request.method == 'POST':
        post_val = request.POST.copy()
        post_val['manager'] = clnt.manager.pk
        form = form_client_add(post_val, instance=clnt)
        if form.is_valid():
            form.save()
        else:
            context_dict = dict(form=form)
            return render_to_response("form_err.html", context_dict)
        url = reverse('person_card', args=(clnt_id, ))
        return HttpResponseRedirect(url)

    context_dict = dict(request=request, clnt=clnt, )
    context_dict.update(csrf(request))
    return render_to_response('client_edit.html', context_dict)


@login_required(login_url='/login')
def photo(request, id):
    try:
        clnt = Client.objects.get(pk=int(id))
    except Client.DoesNotExist:
        context_dict = dict(b_url=reverse('p_active', args=(0, )))
        return render_to_response("clienterr.html", context_dict)
    b_url = reverse('person_card', args=(clnt.pk, ))

    if request.method == 'POST':
        if request.POST["avatar64"]:
            data = request.POST["avatar64"]
            imgName = settings.MEDIA_ROOT + "/avatar/user" + str(time()) + ".png"
            base64_data = re.sub('^data:image/.+;base64,', '', data)
            clnt.avatar.save(
                imgName,
                ContentFile(base64_data.decode('base64')),
                save=True
            )
            clnt.save()
            return HttpResponseRedirect(b_url)

    context_dict = dict(request=request, clnt=clnt, b_url=b_url)
    context_dict.update(csrf(request))
    return render_to_response("client_photo.html", context_dict)


@login_required(login_url='/login')
def search(request, ):
    lst = ""
    if 'query' in request.GET.keys():
        query = request.GET.get('query').upper()
        a_clnts = Contract.objects.filter(is_current__in=[1, 2]).values('client')
        lst = Client.objects.filter(
            last_name__icontains=query
        ).exclude(pk__in=a_clnts).order_by("last_name")
        context_dict = dict(lst=lst, )
        return render_to_response('client_list.html', context_dict)
    elif 'id' in request.GET.keys():
        clnt = Client.objects.get(pk=int(request.GET.get('id')))
        clnt = json.dumps(clnt.as_json())
        return HttpResponse(clnt, mimetype="application/json")
    elif 'is_active' in request.GET.keys():
        clnt = Client.objects.get(pk=int(request.GET.get('is_active')))
        cnt_active = Contract.objects.filter(client=clnt, is_current__in=[1, 2]).count()
        return HttpResponse(json.dumps(dict(res=cnt_active)), mimetype="application/json")


@login_required(login_url='/login')
def client_note(request, clnt_id=0, ):
    try:
        clnt = Client.objects.get(pk=clnt_id)
    except Client.DoesNotExist:
        context_dict = dict(b_url=reverse('p_active', args=(0, )))
        return render_to_response("clienterr.html", context_dict)

    if request.method == 'POST':
        if len(request.POST['note']) > 0:
            clnt.note = request.user.get_full_name() + ': ' + request.POST['note']
        else:
            clnt.note = ''
        clnt.save()
        url = reverse('p_active', args=(0, ))
        return HttpResponseRedirect(url)

    context_dict = dict(request=request, clnt=clnt, b_url=reverse('p_menu'))
    context_dict.update(csrf(request))
    return render_to_response('client_note.html', context_dict)


@login_required(login_url='/login')
def client_ptt(request, clnt_id=0, ):
    try:
        clnt = Client.objects.get(pk=clnt_id)
    except Client.DoesNotExist:
        context_dict = dict(b_url=reverse('p_active', args=(0, )))
        return render_to_response("clienterr.html", context_dict)
    block_visit = 0

    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['date'] = datetime.now()
        post_values['client'] = clnt_id
        post_values['is_card'] = 0
        post_values['user'] = request.user.pk
        f = FormClient_PTT(post_values)
        if f.is_valid():
            f.save()
            post_values['count'] = 1
            post_values['plan_date'] = datetime.now()
            post_values['amount'] = 0
            goods = Goods.objects.get(pk=int(post_values['goods']))
            post_values['department'] = goods.goods_type.pk
            if 'pay_plan' in post_values:
                for i, amount in enumerate(post_values.getlist('pp-price')):
                    delta = i * 30
                    plan_date = datetime.now() + timedelta(days=delta)
                    post_values['plan_date'] = plan_date
                    post_values['amount'] = amount
                    cf = FormCredits(post_values)
                    if cf.is_valid():
                        credit = cf.save()
                        if int(post_values['payment_type']) == 2:
                            credit.close(request.user, 2)
                    else:
                        return HttpResponse(cf.errors, mimetype="text/plain")
                url = reverse('person_card', args=(clnt_id, ))
                return HttpResponseRedirect(url)
            else:
                cf = FormCredits(post_values)
                if cf.is_valid():
                    credit = cf.save()
                    if int(post_values['payment_type']) == 2:
                        credit.close(request.user, 2)
                    url = reverse('person_card', args=(clnt_id, ))
                    return HttpResponseRedirect(url)
                else:
                    return HttpResponse(cf.errors, mimetype="text/plain")
        else:
            return HttpResponse(f.errors, mimetype="text/plain")

    # if have current contract for user
    try:
        contract = Contract.objects.get(client=clnt, is_current=1)
    except Contract.DoesNotExist:
        # if have the prospect contract to activate
        try:
            contract = Contract.objects.get(client=clnt, is_current=2)
        except Contract.DoesNotExist:
            contract = Contract()
            block_visit = 1

    try:
        card = Client_PTT.objects.latest()
        card = card.id + 1 + settings.PTT_START
    except Client_PTT.DoesNotExist:
        card = settings.PTT_START

    contract_visits_left = 0
    contract_days_left = 0
    if not block_visit:
        if contract.days_left() < 8:
            contract_days_left = contract.days_left()
        if contract.contract_type.max_visit < 99999:
            if contract.visits_left() < 5:
                contract_visits_left = contract.visits_left()

    gt = GoodsType.objects.filter(name='PTT')
    ptts = Goods.objects.filter(goods_type__in=gt, is_active=True)
    context_dict = dict(clnt=clnt, request=request, c=clnt,
                        ptts=ptts, block_visit=block_visit, card=card,
                        contract_visits_left=contract_visits_left,
                        contract_days_left=contract_days_left)
    context_dict.update(csrf(request))
    return render_to_response("client_ptt.html", context_dict)


@login_required(login_url='/login')
def prolongation(request, clnt_id=0, act=None):
    if act == 'guest':
        try:
            clnt = rGuest.objects.get(pk=clnt_id)
        except rGuest.DoesNotExist:
            return render_to_response("clienterr.html")
    else:
        try:
            clnt = Client.objects.get(pk=clnt_id)
        except Client.DoesNotExist:
            return render_to_response("clienterr.html")
    try:
        cnumber = Contract.objects.latest()
        cnumber = cnumber.pk + 1 + settings.CNUMBERDELTA
    except Contract.DoesNotExist:
        cnumber = 1 + settings.CNUMBERDELTA
    try:
        contract = Contract.objects.get(client=clnt, is_current=1)
        card = contract.card
        curr_string = contract.contract_type.name + u' '
        curr_string += u' по цене: ' + str(contract.amount)
        if contract.discount:
            curr_string += u' со скидкой: ' + str(contract.discount.value) + '%'
        else:
            curr_string += u' без скидки. '
    except Contract.DoesNotExist:
        contract = Contract()
        card = ""
        curr_string = ''

    if request.method == 'POST':
        post_values = request.POST.copy()
        if act == 'guest':
            try:
                guest = Guest.objects.get(phone=post_values['phone'])
                guest.is_client = 1
                guest.save()
                post_values['manager'] = guest.manager.pk
            except Guest.DoesNotExist:
                post_values['manager'] = request.user.pk
        else:
            post_values['manager'] = clnt.manager.id

        born = strptime(post_values['born_date'], "%d.%m.%Y")
        post_values['born_date'] = date(born.tm_year, born.tm_mon, born.tm_mday)
        ctype = ContractType.objects.get(pk=post_values['contract_type'])

        if clnt.age() >= 14 and not ctype.is_child:
            if act == 'guest':
                form = form_client_add(post_values)
            else:
                form = form_client_add(post_values, instance=clnt)
            if form.is_valid():
                clnt = form.save()
                payer = clnt
            else:
                return HttpResponse(form.errors, mimetype="text/html")
        else:
            try:
                payer = Client.objects.get(first_name=post_values['first_name'].upper(),
                                           last_name=post_values['last_name'].upper(),
                                           patronymic=post_values['patronymic'].upper(),
                                           born_date=post_values['born_date'])
                formp = form_client_add(post_values, instance=payer)
            except Client.DoesNotExist:
                formp = form_client_add(post_values)
            if formp.is_valid():
                payer = formp.save()
            else:
                return HttpResponse(formp.errors, mimetype="text/html")

            # replace values for chilrd
            c_born = strptime(post_values['child_born_date'], "%d.%m.%Y")
            post_values['born_date'] = date(c_born.tm_year, c_born.tm_mon, c_born.tm_mday,)
            post_values['first_name'] = post_values['child_first_name']
            post_values['last_name'] = post_values['child_last_name']
            post_values['patronymic'] = post_values['child_patronymic']
            try:
                clnt = Client.objects.get(
                    first_name=post_values['first_name'].upper(),
                    last_name=post_values['last_name'].upper(),
                    patronymic=post_values['patronymic'].upper(),
                    born_date=post_values['born_date']
                )
                formc = form_client_add(post_values, instance=clnt)
            except Client.DoesNotExist:
                formc = form_client_add(post_values)
            if formc.is_valid():
                clnt = formc.save()

        if act == 'guest':
            g = rGuest.objects.get(pk=clnt_id)
            g.is_client = 1
            g.save()

        if 'discount' in post_values.keys():
            try:
                discount = Discount.objects.get(pk=int(post_values['discount']))
                credit_disc = float(discount.value) / 100
            except Discount.DoesNotExist:
                credit_disc = 0
                discount = Discount()

        if "custom" in post_values.keys():
            pplan = PayPlan(
                name='conter#' + str(time()),
                plantype=2,
                amount=post_values['pp_amount'],
            )
            pplan.save()
            i = 1
            while "price" + str(i) in post_values.keys():
                ppsteps = PayPlanSteps()
                ppsteps.pay_plan = pplan
                ppsteps.amount = post_values['price' + str(i)]
                ppsteps.number = i
                ppsteps.save()
                i += 1
        else:
            if "pay_plan" in post_values.keys():
                try:
                    pplan = PayPlan.objects.get(pk=post_values['pay_plan'])
                except PayPlan.DoesNotExist:
                    pplan = PayPlan()
            else:
                pplan = PayPlan()

        date_start = datetime.now()
        date_end = date_start + timedelta(days=ctype.period_days)

        if "is_open_date" in post_values.keys():
            post_values['is_open_date'] = True
        else:
            post_values['is_open_date'] = False
        post_values['number'] = cnumber
        post_values['date'] = datetime.now()
        post_values['date_start'] = datetime.now()
        post_values['date_end'] = date_end
        post_values['payment_date'] = datetime.now()
        post_values['pay_plan'] = pplan.pk
        post_values['client'] = clnt.pk
        post_values['payer'] = payer.pk
        post_values['is_current'] = 2

        # for contract manager allways is current
        post_values['manager'] = request.user.pk
        cform = form_Contract(post_values)
        if cform.is_valid():
            contract = cform.save()
            if credit_disc > 0:
                contract.discount = discount
                contract.save()
        else:
            res = cform.errors
            return HttpResponseRedirect(res)
        if pplan.pk:
            for step in PayPlanSteps.objects.filter(pay_plan=pplan):
                delta = (step.number - 1) * 30
                if pplan.plantype == 1:
                    amount = (ctype.price - ctype.price * credit_disc) * step.amount / 100
                else:
                    amount = step.amount
                credit = Credits(
                    user=request.user,
                    amount=amount,
                    plan_date=datetime.now() + timedelta(days=delta),
                    contract=contract,
                    payment_type=int(contract.payment_type),
                )
                credit.save()
        else:
            # write single credit
            credit = Credits(
                user=request.user,
                amount=post_values['amount'],
                plan_date=datetime.now(),
                contract=contract,
                payment_type=int(contract.payment_type)
            )
            credit.save()
        url = reverse('pers_cont', args=(clnt.pk, contract.pk))
        return HttpResponseRedirect(url)

    if clnt.age() >= 14:
        ctypes = ContractType.objects.filter(is_active=True)
        payer = clnt
    else:
        ctypes = ContractType.objects.filter(is_active=True, is_child=True)
        payer = Client()

    payplan = PayPlan.objects.filter(is_active=True).exclude(plantype=2)
    discounts = Discount.objects.filter(
        Q(date_start__lte=datetime.now()),
        Q(date_end__gte=datetime.now()) | Q(date_end__isnull=True)
    ).order_by('value')
    context_dict = dict(child=clnt, request=request, ctypes=ctypes, payplan=payplan,
                        cnumber=cnumber, manager=clnt.manager, card=card,
                        discounts=discounts, payer=payer, age=clnt.age(),
                        curr_string=curr_string,
                        )
    context_dict.update(csrf(request))
    return render_to_response("person_prolongation.html", context_dict)


@login_required(login_url='/login')
def person_card(request, clnt_id=0, **kwargs):
    try:
        clnt = Client.objects.get(pk=clnt_id)
    except Client.DoesNotExist:
        return render_to_response("clienterr.html")
    cashhost = settings.CASHIER_HOST
    last_contract = 0
    first_visit = 0
    block_visit = 0
    debts = 0
    visit_time_err = 1
    contract_freeze = ""
    contract_days_left = 0
    contract_visits_left = 0
    has_debts = 0
    # if have current contract for user
    try:
        contract = Contract.objects.get(client=clnt, is_current=1)
    except Contract.DoesNotExist:
        # if have the prospect contract to activate
        try:
            contract = Contract.objects.filter(client=clnt, is_current=2)[0]
            first_visit = contract.number
        except IndexError:
            # check for guestvisit!!!
            contract = Contract()
            contract.client = clnt
            block_visit = 1

    if not block_visit:
        # if contract is find then test for visit time
        debts = Credits.objects.filter(
            contract=contract, plan_date__lte=datetime.now(),
            goods__isnull=True)
        if debts.count() > 0:
            block_visit = 1
        has_debts = Credits.objects.filter(client=clnt_id,
                                           plan_date__lte=datetime.now())
        if contract.contract_type.period_time_type:
            v_start = PeriodTime.objects.get(
                period_time_type=contract.contract_type.period_time_type,
                period_visit_wday=datetime.now().weekday()
            ).period_visit_start
            v_end = PeriodTime.objects.get(
                period_time_type=contract.contract_type.period_time_type,
                period_visit_wday=datetime.now().weekday()
            ).period_visit_end
            if (v_start < datetime.now().time() and v_end > datetime.now().time()):
                visit_time_err = 0

        if contract.is_freeze():
            contract_freeze = contract.freeze_end()

        if contract.days_left() < 8:
            contract_days_left = contract.days_left()
        if contract.contract_type.max_visit < 99999:
            if contract.visits_left() < 5:
                contract_visits_left = contract.visits_left()

        b_url = reverse('p_active', args=(abc.index(clnt.last_name[0]),))
    else:
        last_contract = Contract.objects.filter(client=clnt).order_by('-date')
        if len(last_contract):
            last_contract = last_contract[0]
        b_url = reverse('p_inactive', args=(abc.index(clnt.last_name[0]),))

    if kwargs['act'] == 'change_m':
        m_id = int(request.POST['manager'])
        manager = User.objects.get(pk=m_id)
        clnt.manager = manager
        clnt.save()

    if kwargs['act'] == 'inout':
        clnt.is_online = not clnt.is_online
        if clnt.is_online:
            if contract.is_current == 2:
                contract.activate()
            if contract.is_freeze():
                Freeze.objects.get(
                    contract=contract,
                    is_closed=False,
                    date_end__gte=date.today(),
                    date_start__lte=date.today(),
                ).close()
                contract_freeze = ""

            v = Visits(
                gender=clnt.gender,
                date_start=datetime.now(),
                locker=request.POST['locker'],
                date_end=None,
                contract=contract)
            v.save()
            if contract_visits_left > 0:
                contract_visits_left = int(contract_visits_left) - 1
        else:
            try:
                v = Visits.objects.get(contract=contract, is_online=-1)
                v.out()
                v.save()
                v = ""
            except Visits.DoesNotExist:
                v = ""
            if contract.visits_left() == 0:
                contract.close()
        clnt.save()
        if not clnt.is_online:
            url = reverse('client_login')
            return HttpResponseRedirect(url)
    else:
        try:
            v = Visits.objects.get(contract=contract, is_online=-1)
        except Visits.DoesNotExist:
            v = ""

    clnt_contracts = Contract.objects.filter(client=clnt)
    credits = Credits.objects.filter(contract__in=clnt_contracts)\
                             .order_by('plan_date')
    gcredits = Credits.objects.filter(client=clnt)\
                              .order_by('plan_date')
    c_list = Contract.objects.filter(client=clnt)
    m_list = User.objects.filter(groups__name='manager')  # manual create

    context_dict = dict(clnt=clnt, request=request, block_visit=block_visit,
                        v=v, visit_time_err=visit_time_err, first_visit=first_visit,
                        contract=contract, debts=debts, c_list=c_list,
                        last_contract=last_contract,
                        m_list=m_list, b_url=b_url, has_debts=has_debts,
                        credits=credits, gcredits=gcredits, cashhost=cashhost,
                        contract_visits_left=contract_visits_left,
                        contract_freeze=contract_freeze, contract_days_left=contract_days_left,
                        )
    context_dict.update(csrf(request))
    return render_to_response("client_card.html", context_dict)


@login_required(login_url='/login/')
def person_contract(request, clnt_id=0, contract_id=0):
    res = ""
    # edit exist person with contract
    if clnt_id > 0 and contract_id > 0:
        try:
            contract = Contract.objects.get(id=contract_id, client=clnt_id)
        except Contract.DoesNotExist:
            return render_to_response("print_contracterr.html")
        else:
            try:
                payer = Client.objects.get(pk=contract.payer.id)
                if contract.contract_type.is_child:
                    try:
                        child = Client.objects.get(pk=contract.client.id)
                    except Client.DoesNotExist:
                        return render_to_response("clienterr.html")
                else:
                    child = Client()
            except Client.DoesNotExist:
                return render_to_response("clienterr.html")
            else:
                if request.method == 'POST':
                    post_values = request.POST.copy()
                    post_values['manager'] = request.user.id
                    curr_period = contract.contract_type.period_days

                    # post_values['payment_date'] = datetime.now()
                    born_date = strptime(post_values['born_date'], "%d.%m.%Y")
                    post_values['born_date'] = datetime(
                        born_date.tm_year, born_date.tm_mon, born_date.tm_mday
                    )
                    ctype = ContractType.objects.get(pk=post_values['contract_type'])
                    period_delta = ctype.period_days - curr_period

                    if "custom" in request.POST.keys():
                        if contract.pay_plan and contract.pay_plan.plantype == 2:
                            pplan = contract.pay_plan
                            PayPlanSteps.objects.filter(pay_plan=contract.pay_plan).delete()
                        else:
                            pplan = PayPlan()
                        pplan.name = 'conter#' + str(time())
                        pplan.plantype = 2
                        pplan.amount = post_values['pp_amount']
                        pplan.save()
                        i = 1
                        while "price" + str(i) in post_values.keys():
                            ppsteps = PayPlanSteps()
                            ppsteps.pay_plan = pplan
                            ppsteps.amount = post_values['price' + str(i)]
                            ppsteps.number = i
                            ppsteps.save()
                            i += 1
                    else:
                        if "pay_plan" in request.POST.keys():
                            if contract.pay_plan and contract.pay_plan.plantype == 2:
                                PayPlanSteps.objects.filter(pay_plan=contract.pay_plan.pk).delete()
                                PayPlan.objects.filter(pk=contract.pay_plan.pk).delete()
                            try:
                                pplan = PayPlan.objects.get(pk=post_values['pay_plan'])
                            except PayPlan.DoesNotExist:
                                    pplan = PayPlan()
                        else:
                            pplan = PayPlan()

                    post_values['pay_plan'] = pplan.pk
                    # change photo only by specila function
                    # try:
                    #     img = request.FILES['avatar']
                    #     payer.avatar = img
                    # except MultiValueDictKeyError:
                    #     img = None
                    payer.first_name = post_values['first_name']
                    payer.last_name = post_values['last_name']
                    payer.patronymic = post_values['patronymic']
                    payer.gender = int(post_values['gender'])
                    payer.phone = post_values['phone']
                    payer.born_date = post_values['born_date']
                    payer.address = post_values['address']
                    payer.email = post_values['email']
                    payer.passport = post_values['passport']
                    # clnt.manager=request.user

                    try:
                        payer.save()
                    except:
                        res = 'Такой пользователь уже существует'
                        # return render_to_response("clienterr.html")
                    if ctype.is_child:
                        child_born_date = strptime(post_values['child_born_date'], "%d.%m.%Y")
                        post_values['child_born_date'] = datetime(
                            child_born_date.tm_year,
                            child_born_date.tm_mon,
                            child_born_date.tm_mday
                        )
                        if contract.contract_type.is_child:
                            child.first_name = post_values['child_first_name']
                            child.last_name = post_values['child_last_name']
                            child.patronymic = post_values['child_patronymic']
                            child.born_date = post_values['child_born_date']
                        else:
                            child = Client(
                                first_name=post_values['child_first_name'],
                                last_name=post_values['child_last_name'],
                                patronymic=post_values['child_patronymic'],
                                born_date=post_values['child_born_date'],
                                manager=request.user,
                            )
                        child.save()
                        clnt = child
                    else:
                        clnt = payer

                    try:
                        discount = Discount.objects.get(pk=int(post_values['discount']))
                        credit_disc = float(discount.value) / 100
                    except Discount.DoesNotExist:
                        discount = Discount()
                        credit_disc = 0
                    if "is_open_date" in request.POST.keys():
                        post_values['is_open_date'] = True
                    else:
                        post_values['is_open_date'] = False

                    contract.manager = request.user
                    contract.date_start = contract.date_start
                    end_delta = timedelta(days=period_delta)
                    contract.date_end = contract.date_end + end_delta
                    contract.contract_type = ctype
                    contract.card = post_values['card']
                    contract.discount = discount
                    contract.amount = post_values['amount']
                    contract.pay_plan = pplan
                    contract.payment_type = int(post_values['payment_type'])
                    contract.payment_date = datetime.now()
                    contract.client = clnt
                    contract.payer = payer
                    contract.is_open_date = post_values['is_open_date']
                    contract.save()
                    # save all real payments
                    ch_summ = CreditsHistory.objects.filter(
                        contract=contract
                    ).aggregate(models.Sum('amount'))
                    Credits.objects.filter(contract=contract).delete()

                    if pplan.pk:
                        for step in PayPlanSteps.objects.filter(pay_plan=pplan):
                            delta = (step.number - 1) * 30
                            if pplan.plantype == 1:
                                price = ctype.price - ctype.price * credit_disc
                                amount = price * step.amount / 100
                            else:
                                amount = step.amount
                            credit = Credits(
                                user=request.user,
                                amount=amount,
                                plan_date=contract.date + timedelta(days=delta),
                                contract=contract,
                                payment_type=contract.payment_type,
                            )
                            credit.save()
                    else:
                        # write single credit
                        credit = Credits(
                            user=request.user,
                            amount=post_values['amount'],
                            plan_date=contract.date,
                            contract=contract,
                            payment_type=contract.payment_type
                        )
                        credit.save()
                    # close debts, that was in credits history
                    if ch_summ['amount__sum'] > 0:
                        for p in Credits.objects.filter(contract=contract).order_by('plan_date'):
                            if p.amount <= ch_summ['amount__sum']:
                                p.delete()
                                ch_summ['amount__sum'] -= p.amount
                            elif ch_summ['amount__sum'] > 0:
                                p.amount -= ch_summ['amount__sum']
                                ch_summ['amount__sum'] = 0
                                p.save()
                                break
                else:
                    pass

                manager = payer.manager.get_full_name()
                payplan = PayPlan.objects.filter(is_active=True).exclude(plantype=2)
                ctypes = ContractType.objects.filter(is_active=True)

                if not contract.contract_type.is_active:
                    ctypes = ctypes | ContractType.objects.filter(pk=contract.contract_type.pk)

                if contract.pay_plan and contract.pay_plan.plantype == 2:
                    ppsteps = PayPlanSteps.objects.filter(pay_plan=contract.pay_plan)
                else:
                    ppsteps = PayPlanSteps()

                discounts = Discount.objects.filter(
                    Q(date_start__lte=datetime.now()),
                    Q(date_end__gte=datetime.now()) | Q(date_end__isnull=True)
                ).order_by('value')

                if contract.discount:
                    discounts = discounts | Discount.objects.filter(pk=contract.discount.pk)

                context_dict = dict(clnt_id=clnt_id, contract=contract, manager=manager,
                                    child=child,
                                    discounts=discounts, ppsteps=ppsteps, request=request,
                                    clnt=payer, ctypes=ctypes, payplan=payplan, res=res)

                context_dict.update(csrf(request))
                return render_to_response("person_contract.html", context_dict, )


@login_required(login_url='/login/')
def person_menu(request, letter=0, **kwargs):
    lst = []
    if kwargs['act'] == 'active':
        c = Contract.objects.filter(is_current=1).values('client')
        clnts = Client.objects.filter(pk__in=c,).order_by("last_name")
        url = "active"
    elif kwargs['act'] == 'inactive':
        c = Contract.objects.filter(is_current__in=[1, 2]).values('client')
        clnts = Client.objects.exclude(pk__in=c).order_by("last_name")
        url = "inactive"
    else:
        clnts = Client.objects.all().order_by("last_name")
        url = "menu"

    if letter > 0:
        clnts = clnts.filter(last_name__istartswith=abc[int(letter)]).order_by("last_name")

    if 'query' in request.GET.keys():
        query = request.GET.get('query')
        clnts = Client.objects.filter(last_name__icontains=query).order_by("last_name")

    for clnt in clnts:
        curr_contract = 0
        clnt_contracts = Contract.objects.filter(client=clnt)
        if clnt_contracts.count():
            try:
                curr_contract = Contract.objects.get(client=clnt, is_current=1).pk
            except Contract.DoesNotExist:
                pass

        lst.append((clnt, curr_contract, clnt_contracts))

    context_dict = dict(lst=lst, request=request, abc=abc, url=url)
    return render_to_response("person_menu.html", context_dict, )


@login_required(login_url='/login/')
def person_add(request,):
    # new person contract add
    res = ""
    manager = request.user.get_full_name()
    ctypes = ContractType.objects.filter(is_active=True)
    payplan = PayPlan.objects.filter(is_active=True).exclude(plantype=2)
    try:
        cnumber = Contract.objects.latest()
        cnumber = cnumber.pk + 1 + settings.CNUMBERDELTA
    except Contract.DoesNotExist:
        cnumber = 1 + settings.CNUMBERDELTA

    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['manager'] = request.user.id
        contract = Contract()

        post_values['payment_date'] = datetime.now()
        born_date = strptime(post_values['born_date'], "%d.%m.%Y")
        post_values['born_date'] = datetime(
            born_date.tm_year,
            born_date.tm_mon,
            born_date.tm_mday
        )
        ctype = ContractType.objects.get(pk=post_values['contract_type'])
        post_values['date_start'] = datetime.now()
        post_values['date'] = datetime.now()
        post_values['date_end'] = datetime.now() + timedelta(days=ctype.period_days)

        if "custom" in request.POST.keys():
            pplan = PayPlan()
            pplan.name = 'contr#' + str(cnumber + time())
            pplan.plantype = 2
            pplan.amount = post_values['pp_amount']
            pplan.save()
            i = 1
            while "price" + str(i) in post_values.keys():
                ppsteps = PayPlanSteps()
                ppsteps.pay_plan = pplan
                ppsteps.amount = post_values['price' + str(i)]
                ppsteps.number = i
                ppsteps.save()
                i += 1
        else:
            if "pay_plan" in request.POST.keys():
                try:
                    pplan = PayPlan.objects.get(pk=post_values['pay_plan'])
                except PayPlan.DoesNotExist:
                    pplan = PayPlan()
            else:
                pplan = PayPlan()

        post_values['pay_plan'] = pplan.pk
        if not post_values['card']:
            post_values['card'] = '0'
        cform = form_Contract(post_values)

        form = form_client_add(post_values)
        if form.is_valid():
            res = "Form person OK"
            try:
                guest = Guest.objects.get(phone=post_values['phone'])
                guest.is_client = 1
                guest.save()
                manager = guest.manager
            except Guest.DoesNotExist:
                manager = request.user
            clnt = Client(
                first_name=post_values['first_name'],
                last_name=post_values['last_name'],
                patronymic=post_values['patronymic'],
                gender=post_values['gender'],
                phone=post_values['phone'],
                born_date=post_values['born_date'],
                address=post_values['address'],
                email=post_values['email'],
                passport=post_values['passport'],
                manager=manager,
            )
            clnt.save()
            payer = clnt  # payer always is Client fields in form
            if ctype.is_child:
                child_born_date = strptime(post_values['child_born_date'], "%d.%m.%Y")
                post_values['child_born_date'] = datetime(
                    child_born_date.tm_year,
                    child_born_date.tm_mon,
                    child_born_date.tm_mday,
                )
                clnt = Client(
                    first_name=post_values['child_first_name'],
                    last_name=post_values['child_last_name'],
                    patronymic=post_values['child_patronymic'],
                    born_date=post_values['child_born_date'],
                    manager=manager,
                )
                clnt.save()
            if request.POST["avatar64"]:
                imgName = settings.MEDIA_ROOT + "/avatar/user" + str(time()) + ".png"
                clnt.avatar.save(
                    imgName, ContentFile(post_values['avatar64'].decode('base64')), save=True
                )

            post_values['client'] = clnt.id
            post_values['payer'] = payer.id
            if "is_open_date" in request.POST.keys():
                post_values['is_open_date'] = True
            else:
                post_values['is_open_date'] = False

            # form.save()
            if cform.is_valid():
                res += " Form contract OK"
                # cform.save()
                try:
                    discount = Discount.objects.get(pk=int(post_values['discount']))
                    credit_disc = float(discount.value) / 100
                except Discount.DoesNotExist:
                    credit_disc = 0
                    discount = Discount()
                contract = Contract(
                    number=post_values['number'],
                    manager=request.user,
                    date_start=post_values['date_start'],
                    date_end=post_values['date_end'],
                    contract_type=ctype,
                    card=post_values['card'],
                    discount=discount,
                    amount=post_values['amount'],
                    pay_plan=pplan,
                    payment_type=post_values['payment_type'],
                    is_open_date=post_values['is_open_date'],
                    payment_date=datetime.now(),
                    client=clnt,
                    payer=payer,
                    # wait for the activation
                    is_current=2,
                )
                contract.save()
                if pplan.pk:
                    for step in PayPlanSteps.objects.filter(pay_plan=pplan):
                        delta = (step.number - 1) * 30
                        if pplan.plantype == 1:
                            price = ctype.price - ctype.price * credit_disc
                            amount = price * step.amount / 100
                        else:
                            amount = step.amount
                        credit = Credits(
                            user=request.user,
                            amount=amount,
                            plan_date=datetime.now() + timedelta(days=delta),
                            contract=contract,
                            payment_type=int(contract.payment_type),
                        )
                        credit.save()
                else:
                    # write single credit
                    credit = Credits(
                        user=request.user,
                        amount=post_values['amount'],
                        plan_date=datetime.now(),
                        contract=contract,
                        payment_type=int(contract.payment_type),
                    )
                    credit.save()

                url = '/person/' + str(clnt.id) + '/' + str(contract.id)
                return HttpResponseRedirect(url)
            else:
                clnt.delete()
                context_dict = dict(res=res, form=form, cform=cform, request=request,)
                return render_to_response("person_add.html", context_dict)
        else:
            discounts = Discount.objects.filter(
                Q(date_start__lte=datetime.now()),
                Q(date_end__gte=datetime.now()) | Q(date_end__isnull=True)
            ).order_by('value')
    else:
        form = form_client_add()
        cform = form_Contract()
        contract = Contract()
        discounts = Discount.objects.filter(
            Q(date_start__lte=datetime.now()),
            Q(date_end__gte=datetime.now()) | Q(date_end__isnull=True)
        ).order_by('value')

    context_dict = dict(
        form=form, cform=cform, cnumber=cnumber, contract=contract,
        discounts=discounts, request=request,
        manager=manager, ctypes=ctypes, payplan=payplan, res=res
    )
    context_dict.update(csrf(request))
    return render_to_response("person_add.html", context_dict)
