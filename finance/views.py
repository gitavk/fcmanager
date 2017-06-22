# -*- coding: utf-8 -*-
import urllib2
from time import strptime
from datetime import date, datetime
from decimal import Decimal
import json

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.db.models import ProtectedError, Avg, Max, Min
from django.db.models import F
from django.conf import settings

from person.models import Client
from reception.models import Guest
from employees.models import Position, Employee, WorkRecord, DepartmentPosition
from .models import *
from .dbmodels import *
from .forms import *

departments = settings.DEPARTMENTS
# not true goods type
excl_gt = GoodsType.objects.filter(name__in=['PTT'])
excl_g = Goods.objects.filter(goods_type__in=excl_gt, is_pay_freeze=True)

@login_required(login_url='/login')
def ptt_trainer(request):
    goods = Goods.objects.get(pk=request.GET['id'])
    positions = PositionPTT.objects.filter(goods=goods).values('position')
    w_pos = DepartmentPosition.objects.filter(position__in=positions)
    trainers = dict()
    for t in WorkRecord.objects.filter(wposition__in=w_pos):
        trainers[t.employee.pk] = t.employee.get_full_name()

    res = json.dumps(trainers)
    return HttpResponse(res, content_type="application/json")

@login_required(login_url='/login')
def ptt_card(request, id=0, ):
    p_title = u'персональная тренировка '
    if id:
        try:
            ptt = Client_PTT.objects.get(pk=int(id))
            p_title += u'номер ' + str(ptt.number())
            p_title += ':   ' + ptt.client.initials()
            b_url = reverse('reports_menu')
        except Client_PTT.DoesNotExist:
            b_url = reverse('p_active', args=(0, ))
            context_dict = dict(request=request, p_title=p_title, b_url=b_url)
            return render_to_response("err404.html", context_dict)

        if request.method == 'POST':
            ptt.is_card = 1
            ptt.save()
            return HttpResponseRedirect(b_url)
    context_dict = dict(request=request, b_url=b_url, p_title=p_title,
                    ptt=ptt)
    context_dict.update(csrf(request))
    return render_to_response('ptt_card.html', context_dict)

@login_required(login_url='/login')
def ptt(request, id=0, act=None ):
    p_title = "Персональные тренировки"
    b_url = reverse('ptt')
    sysgt = GoodsType.objects.filter(name__in=['PTT', '1PTT'])
    if act == 'add':
        p_title = "Новый вид ПТТ"
        form = FormGoods()
        if request.method == 'POST':
            post_values = request.POST.copy()
            post_values['single_visit'] = 0
            post_values['client_only'] = 0
            if "1ptt" in request.POST.keys():
                gt = GoodsType.objects.get(name='1PTT')
            else:
                gt = GoodsType.objects.get(name='PTT')
            if "is_discount" in request.POST.keys():
                post_values['is_discount'] = 1
            else:
                post_values['is_discount'] = 0
            post_values['goods_type'] = gt.pk
            post_values['pay_days'] = 0
            form = FormGoods(post_values)
            if form.is_valid():
                g = form.save()
                for p in request.POST.getlist('positions'):
                    position = Position.objects.get(pk=int(p))
                    PositionPTT(position=position, goods=g).save()

                if request.POST['price']:
                    date_s = strptime(request.POST['date_start'],"%d.%m.%Y")
                    date_s = date(date_s.tm_year,date_s.tm_mon,date_s.tm_mday,)
                    g.new_price(request.POST['price'], date_s)
                    
                if 'bar_code' in request.POST.keys():
                    if request.POST['bar_code'].strip() != '':
                        try:
                            code=Decimal(request.POST['bar_code'])
                            bar_code = BarCode(goods=g,code=code)
                            bar_code.save()
                        except ValueError:
                            pass
                return HttpResponseRedirect(b_url)
        positions = Position.objects.all()
        context_dict = dict(request=request, p_title=p_title, b_url=b_url,
                          departments=departments, form=form,
                          positions=positions)
        context_dict.update(csrf(request))
        return render_to_response("ptt_add.html", context_dict)
    elif id > 0:
        try:
            g = Goods.objects.get(pk=id)
        except Goods.DoesNotExist:
            o_name = "ПТТ"
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if act == 'del':
                Price.objects.filter(goods=g).delete()
                BarCode.objects.filter(goods=g).delete()
                g.delete()
        elif act == 'edit':
            p_title = "Персональная тренировка"
            if request.method == 'POST':
                post_values = request.POST.copy()
                post_values['single_visit'] = 0
                post_values['client_only'] = 0
                if "1ptt" in request.POST.keys():
                    gt = GoodsType.objects.get(name='1PTT')
                else:
                    gt = GoodsType.objects.get(name='PTT')
                if "is_discount" in request.POST.keys():
                    post_values['is_discount'] = 1
                else:
                    post_values['is_discount'] = 0
                post_values['goods_type'] = gt.pk
                post_values['pay_days'] = 0
                form = FormGoods(post_values, instance=g)
                if form.is_valid():
                    form.save()
                if request.POST['price']:
                    new_price = Decimal(request.POST['price'])
                    if g.price() != new_price:
                        date_s = strptime(request.POST['date_start'],"%d.%m.%Y")
                        date_s = date(date_s.tm_year,date_s.tm_mon,date_s.tm_mday,)
                        g.new_price(request.POST['price'], date_s)

                BarCode.objects.filter(goods=g).delete()
                if 'bar_code' in request.POST.keys():
                    if request.POST['bar_code'].strip() != '':
                        try:
                            code=Decimal(request.POST['bar_code'])
                            bar_code = BarCode(goods=g, code=code)
                            bar_code.save()
                        except ValueError:
                            pass

                PositionPTT.objects.filter(goods=g).delete()
                for p in request.POST.getlist('positions'):
                    position = Position.objects.get(pk=int(p))
                    PositionPTT(position=position, goods=g).save()

                return HttpResponseRedirect(b_url)
            price = Price.objects.filter(goods=g)
            try:
                bcode = BarCode.objects.get(goods=g)
            except BarCode.DoesNotExist:
                bcode = ""

            positions = Position.objects.all()
            ptt_positions = PositionPTT.objects.filter(goods=g).values_list('position', flat=True)
            context_dict = dict(request=request, p_title=p_title, g=g, b_url=b_url,
                                departments=departments, edit=1, price=price,
                                bcode=bcode, ptt_positions=ptt_positions,
                                positions=positions)
            context_dict.update(csrf(request))
            return render_to_response("ptt_add.html", context_dict)
    lst = Goods.objects.filter(goods_type__in=sysgt).order_by('name')
    context_dict = dict(request=request, lst=lst, p_title=p_title)
    return render_to_response("ptt.html", context_dict)

@login_required(login_url='/login')
def esc_credit(request, ):
    if 'cr_id' in request.GET.keys():
        cr = Credits.objects.get(pk=int(request.GET['cr_id']))
        try:
            cr.escape()
            return HttpResponse(json.dumps(dict(res=-1)), content_type="application/json")
        except Exception, e:
            return HttpResponse(json.dumps(dict(res=-1)), content_type="application/json")
    elif 'ch_id' in request.GET.keys():
        ch = CashCheck.objects.get(pk=int(request.GET['ch_id']))
        if ch.cash_rollback() == 1:
            try:
                ch.rollback()
                return HttpResponse(json.dumps(dict(res=1)), content_type="application/json")
            except Exception, e:
                return HttpResponse(json.dumps(dict(res=-1)), content_type="application/json")

@login_required(login_url='/login')
def close_credit(request, ):
    if 'oway' in request.GET.keys():
        crid = urllib2.unquote(request.GET['crid'].encode('utf-8'))
        crid = int(crid)
        Credits.objects.get(pk=crid).close(request.user, 2)
        res = "1"
    elif 'crlist' in request.GET.keys():
        crlist = urllib2.unquote(request.GET['crlist'].encode('utf-8'))
        pay_type = urllib2.unquote(request.GET['chtype'].encode('utf-8'))
        pay_type = int(pay_type)
        # change cashier pay type into pay type of the database
        if pay_type == 1:
            pay_type = 0
        elif pay_type == 2:
            pay_type = 1
        crlist = crlist.split('|')
        cc = CashCheck()
        cc.save()
        for x in range(0,(len(crlist)-1)/5):
            crid = int(crlist[x*5][2:])
            if crid == 0:
                # single cash payment
                cnt = int(crlist[x*5+2])
                glist = urllib2.unquote(request.GET['glist'].encode('utf-8')).split('|')
                gid = int(glist[x])
                g = Goods.objects.get(pk=gid)
                amount = g.price() * cnt
                ch = CreditsHistory(
                    user=request.user, amount=amount,
                    plan_date=datetime.now(), goods=g, count=cnt,
                    payment_user=request.user, payment_type=pay_type,
                    department=g.department, check=cc)
                ch.save()
                invoice = InvoiceGoods.objects.filter(goods=g).order_by('expirydate')
                for ig in IssuanceGoods.objects.filter(goods__in=invoice, balance__gt=0):
                    if cnt > ig.balance:
                        cnt -= ig.balance
                        ig.balance = 0
                        ig.save()
                    else:
                        ig.balance -= cnt
                        ig.save()
                        break
            else:
                Credits.objects.get(pk=crid).close(request.user, pay_type, cc)
        res = "1"
    else:
        res = "0"

    context_dict = dict(res=res)
    return render_to_response("close_credit.html", context_dict)

@login_required(login_url='/login')
def hasitinvite(request, clnt=0, act=None,):
    res=0
    callback = request.GET['callback']
    if act == 'client':
        try:
            clnt = Client.objects.get(pk=clnt)
            if Invitation.objects.filter(client=clnt, is_free=True).count() > 0:
                res = 1
            elif Contract.objects.filter(client=clnt, is_current__in=[1, 2]).count() > 0:
                res = 1
        except Client.DoesNotExist:
            pass
    else:
        try:
            clnt = Guest.objects.get(pk=clnt)
            if Invitation.objects.filter(guest=clnt, is_free=True).count() > 0:
                res = 1
        except Guest.DoesNotExist:
            pass
    context_dict = dict(res=res, callback=callback)
    return render_to_response('has_invite.html', context_dict)

@login_required(login_url='/login')
def credit(request, clnt=0, b_url=None,):
    res = ""
    if request.method == 'GET':
        if 'gqeury' in request.GET.keys():
            gqeury = request.GET['gqeury']
            try:
                find = Decimal(gqeury)
            except Exception, e:
                find = gqeury

            if isinstance(find, Decimal):
                try:
                    res = BarCode.objects.filter(code=find).exclude(goods__in=excl_g)[0].goods
                    cnt = 1
                except IndexError:
                    res = ""
                    cnt = 0
            else:
                res = Goods.objects.filter(name__icontains=find).exclude(pk__in=excl_g)
                cnt = res.count()
                if cnt == 1:
                    res = res[0]
            context_dict = dict(res=res, cnt=cnt, f=find)
            return render_to_response('goods_list.html', context_dict)

        elif 'clnquery' in request.GET.keys():
            try:
                find = long(request.GET.get('clnquery'))
            except ValueError:
                find = request.GET.get('clnquery')

            if isinstance(find, long):
                clients = Contract.objects.filter(card=find, is_current=1).values('client')
                res = Client.objects.filter(pk__in=clients)
                gres = 0
                cnt = res.count()
            else:
                res = Client.objects.filter(last_name__icontains=find)
                gres = Guest.objects.filter(lastname__icontains=find)
                cnt = res.count() + gres.count()

            if cnt == 1:
                try:
                    res = res[0]
                    gres = 0
                except IndexError:
                    gres = gres[0]
                    res = 0
            context_dict = dict(res=res, gres=gres, cnt=cnt, f=find)
            return render_to_response('clients_list.html', context_dict)

    if clnt > 0:
        if b_url == 'r_guest_card':
            try:
                clnt = Guest.objects.get(pk=clnt)
            except Guest.DoesNotExist:
                pass
        else:
            try:
                clnt = Client.objects.get(pk=clnt)
            except Client.DoesNotExist:
                pass
    else:
        if request.method == 'POST':
            cashhost = settings.CASHIER_HOST
            amount = 0
            lst = []
            g_values = {}
            post_values = request.POST.copy()
            for i in range(int(post_values['goods_cnt'])+1):
                if 'cnt' + str(i) in post_values.keys():
                    count = int(post_values['cnt' + str(i)])
                    g = Goods.objects.get(pk = int(post_values['g' + str(i)]))
                    if 'trainer' + str(i) in post_values.keys():
                        g_values['employee'] = post_values['trainer' + str(i)]
                    else:
                        g_values['employee'] = ''
                    lst.append((g, count))
                    amount += g.price() * count
            context_dict = dict(request=request, lst=lst, amount=amount,
                    cashhost=cashhost)
            return render_to_response('single_credit.html', context_dict)

    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['user'] = request.user.pk
        post_values['amount'] = 0
        post_values['plan_date'] = datetime.now()
        post_values['payment_type'] = 0
        for i in range(int(post_values['goods_cnt'])+1):
            if 'cnt' + str(i) in post_values.keys():
                post_values['goods'] = post_values['g' + str(i)]
                post_values['count'] = post_values['cnt' + str(i)]
                g = Goods.objects.get(pk = int(post_values['goods']))
                post_values['department'] = g.department
                if 'trainer' + str(i) in post_values.keys():
                    post_values['employee'] = post_values['trainer' + str(i)]
                else:
                    post_values['employee'] = ''
                f = FormCredits(post_values)
                if f.is_valid():
                    res = f.save()
                else:
                    res = f.errors
        return HttpResponseRedirect(reverse(b_url, args=(clnt.pk,)))

    context_dict = dict(request=request, clnt=clnt, b_url=b_url, res=res,)
    context_dict.update(csrf(request))
    return render_to_response('client_credit.html', context_dict)

@login_required(login_url='/login')
def service(request, id=0, act=None ):
    p_title = "Услуги"
    b_url = reverse('service')
    sysgt = GoodsType.objects.filter(name='SERVICE')
    if act == 'add':
        p_title = "Новая услуга"
        form = FormGoods()
        if request.method == 'POST':
            post_values = request.POST.copy()
            gt = GoodsType.objects.get(name='SERVICE')
            post_values['goods_type'] = gt.pk
            if "client_only" in request.POST.keys():
                post_values['client_only'] = 1
            else:
                post_values['client_only'] = 0
            if "single_visit" in request.POST.keys():
                post_values['single_visit'] = 1
            else:
                post_values['single_visit'] = 0
            post_values['is_discount'] = 0
            post_values['pay_days'] = 0
            form = FormGoods(post_values)
            if form.is_valid():
                g = form.save()
                if request.POST['price']:
                    date_s = strptime(request.POST['date_start'],"%d.%m.%Y")
                    date_s = date(date_s.tm_year,date_s.tm_mon,date_s.tm_mday,)
                    g.new_price(request.POST['price'], date_s)
                if 'bar_code' in request.POST.keys():
                    if request.POST['bar_code'].strip() != '':
                        try:
                            code=Decimal(request.POST['bar_code'])
                            bar_code = BarCode(goods=g,code=code)
                            bar_code.save()
                        except Exception, e:
                            pass
                        
                return HttpResponseRedirect(b_url)

        context_dict = dict(request=request, p_title=p_title, b_url=b_url,
                         departments=departments, form=form)
        context_dict.update(csrf(request))
        return render_to_response("service_add.html", context_dict)
    elif id > 0:
        try:
            g = Goods.objects.get(pk=id)
        except Goods.DoesNotExist:
            o_name = "Услуга"
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if act == 'del':
                Price.objects.filter(goods=g).delete()
                BarCode.objects.filter(goods=g).delete()
                g.delete()
        elif act == 'edit':
            p_title = "Услуга"
            if request.method == 'POST':
                post_values = request.POST.copy()
                if "client_only" in request.POST.keys():
                    post_values['client_only'] = 1
                else:
                    post_values['client_only'] = 0
                if "single_visit" in request.POST.keys():
                    post_values['single_visit'] = 1
                else:
                    post_values['single_visit'] = 0
                post_values['is_discount'] = 0
                post_values['pay_days'] = 0
                form = FormGoods(post_values, instance=g)
                if form.is_valid():
                    form.save()
                if request.POST['price']:
                    new_price = Decimal(request.POST['price'])
                    if g.price() != new_price:
                        date_s = strptime(request.POST['date_start'],"%d.%m.%Y")
                        date_s = date(date_s.tm_year,date_s.tm_mon,date_s.tm_mday,)
                        g.new_price(request.POST['price'], date_s)

                BarCode.objects.filter(goods=g).delete()
                if 'bar_code' in request.POST.keys():
                    if request.POST['bar_code'].strip() != '':
                        try:
                            code=Decimal(request.POST['bar_code'])
                            bar_code = BarCode(goods=g, code=code)
                            bar_code.save()
                        except Exception, e:
                            pass

                return HttpResponseRedirect(b_url)
            price = Price.objects.filter(goods=g)
            try:
                bcode = BarCode.objects.get(goods=g)
            except BarCode.DoesNotExist:
                bcode = ""
            
            context_dict = dict(request=request, p_title=p_title, g=g, b_url=b_url,
                                departments=departments, edit=1, price=price,
                                bcode=bcode)
            context_dict.update(csrf(request))
            return render_to_response("service_add.html", context_dict)

    lst = Goods.objects.filter(goods_type__in=sysgt).order_by('name')
    context_dict = dict(request=request, lst=lst, p_title=p_title)
    return render_to_response("services.html", context_dict)

@login_required(login_url='/login')
def warehouse_goods(request, ):
    lst = InvoiceGoods.objects.filter(balance__gt=0).order_by('expirydate')
    context_dict = dict(request=request, lst=lst)
    return render_to_response("warehouse_goods.html", context_dict)

@login_required(login_url='/login')
def trash_goods_del(request,):
    tgpk = int(request.GET['id'])
    g = TrashGoods.objects.get(pk=tgpk)
    for vig in vIssuanceGoodsRecovery.objects.filter(
                                                    goods=g.goods).order_by(
                                                    '-expirydate'):
        ig = IssuanceGoods.objects.get(pk=vig.pk)
        if (ig.count - ig.balance) >= g.count:
            ig.balance += g.count
            ig.save()
            g.delete()
            break
        elif (ig.count - ig.balance) < g.count:
            g.count -= ig.count - ig.balance
            ig.balance = ig.count
            ig.save()
    res = json.dumps(dict(res=1))
    return HttpResponse(res, content_type="application/json")

@login_required(login_url='/login')
def trash(request, id=0, act=None):
    res = ""
    p_title = "Накладная на списание"
    def add_trash_goods(gcnt):
        for i in range(gcnt+1):
            if "cnt" + str(i) in post_values.keys():
                try:
                    count = int(post_values['cnt' + str(i)])
                except ValueError:
                    res = res + ' ValueError'
                    continue 
                if count < 1:
                    res = res + ' count < 1'
                    continue
                g_pk = int(post_values['goods'+ str(i)])
                for vig in vIssuanceGoods.objects.filter(goods=g_pk
                                                ).order_by('expirydate'):
                    ig = IssuanceGoods.objects.get(pk=vig.pk)
                    if ig.balance >= count:
                        ig.balance -= count
                        trash_cnt = count
                        count = 0
                    elif ig.balance < count:
                        trash_cnt = ig.balance
                        count -= ig.balance
                        ig.balance = 0
                    ig.save()
                    note = post_values['note' + str(i)]
                    tg = TrashGoods(trash=t, goods=vig.goods
                                   , count=trash_cnt, note=note)
                    tg.save()
                    if count == 0:
                        break
    if act == 'add':
        if request.method == 'POST':
            post_values = request.POST.copy()
            post_values['manager'] = request.user.pk
            post_values['date'] = datetime.now()
            f = FormTrash(post_values)
            if f.is_valid():
                t = f.save()
            else:
                print (f.errors)
            add_trash_goods(int(post_values['goods_cnt']))
            return HttpResponseRedirect (reverse('trash'))
        else:
            last = Trash.objects.filter(date__year=datetime.now().year
                                        ).aggregate(Max('pk'))
            if last['pk__max']:
                number = last['pk__max'] + 1
            else:
                number = 1
            p = Market.objects.all()
            context_dict = dict(request=request, p_title=p_title, p=p, res=res,
                                number=number, )
            context_dict.update(csrf(request))
            return render_to_response("trash_form.html", context_dict)        
    elif act == 'del':
        tpk = int(request.GET['id'])
        t = Trash.objects.get(pk=tpk)
        for g in TrashGoods.objects.filter(trash=t):
            for vig in vIssuanceGoodsRecovery.objects.filter(
                                                    goods=g.goods).order_by(
                                                    '-expirydate'):
                ig = IssuanceGoods.objects.get(pk=vig.pk)
                if (ig.count - ig.balance) >= g.count:
                    ig.balance += g.count
                    ig.save()
                    g.delete()
                    break
                elif (ig.count - ig.balance) < g.count:
                    g.count -= ig.count - ig.balance
                    ig.balance = ig.count
                    ig.save()
        t.delete()
        res = json.dumps(dict(res=1))
        return HttpResponse(res, content_type="application/json")
    elif act == 'edit':
        tpk = int(id)
        t = Trash.objects.get(pk=tpk)
        if request.method == 'POST':
            post_values = request.POST.copy()
            add_trash_goods(int(post_values['goods_cnt']))
            return HttpResponseRedirect (reverse('trash'))
        marketgoods = []
        i = Issuance.objects.filter(market=t.market).values('pk')
        ig = IssuanceGoods.objects.filter(balance__gt=0, issuance__in=i
                                            ).values('goods')
        glst = InvoiceGoods.objects.filter(pk__in=ig).values('goods')
        for g in Goods.objects.filter(pk__in=glst).order_by('name'):
            if g.on_market() > 0:
                marketgoods.append(g)
        context_dict = dict(request=request, p_title=p_title, trash=t,
                        marketgoods=marketgoods)
        context_dict.update(csrf(request))
        return render_to_response("trash_edit.html", context_dict)
    lst = []
    trash = Trash.objects.all().order_by('-id')
    but_all = 0
    for t in trash:
        goods = TrashGoods.objects.filter(trash=t)
        lst.append((t, goods))
    context_dict = dict(request=request, but_all=but_all, lst=lst, res=res)
    context_dict.update(csrf(request))
    return render_to_response("trash.html", context_dict)

@login_required(login_url='/login')
def issuance(request, id=0, act=None):
    res = ""
    p_title = "Внутренняя накладная"
    form = FormInvoice()
    if act == 'add':
        if request.method == 'POST':
            post_values = request.POST.copy()
            post_values['manager'] = request.user.pk
            idate = strptime(post_values['date'],"%d.%m.%Y")
            post_values['date'] = date(idate.tm_year, idate.tm_mon, idate.tm_mday,)
            form = FormIssuance(post_values)
            if form.is_valid():
                issuance = form.save()
                total = 0
                for i in range(int(post_values['goods_cnt'])+1):
                    post_values['issuance'] = issuance.pk
                    if "cnt" + str(i) in post_values.keys():
                        try:
                            count = int(post_values['cnt' + str(i)])
                        except ValueError:
                            res = res + ' ValueError'
                            continue 
                        if count < 1:
                            res = res + ' count < 1'
                            continue
                        postg = int(post_values['goods' + str(i)])
                        # get goods from warehouse by invoices
                        for g in InvoiceGoods.objects.filter(goods=postg, balance__gt=0
                                                            ).order_by('expirydate'):
                            if count > g.goods.in_stock():
                                res = res + ' Превышено количество товаров на складе'
                                IssuanceGoods.objects.filter(issuance=issuance).delete()
                                Issuance.objects.filter(pk=issuance.pk).delete()
                                break
                            if count > g.balance:
                                post_values['count'] = g.balance
                                count -= g.balance
                            else:
                                post_values['count'] = count
                                count = 0
                            post_values['goods'] = g.id
                            post_values['note'] = post_values['note' + str(i)]
                            post_values['balance'] = post_values['count']
                            gform = FormIssuanceGoods(post_values)
                            if gform.is_valid():
                                IssuanceGoods(issuance = issuance,
                                    goods = g,
                                    count = post_values['count'],
                                    note = post_values['note'],
                                    balance = post_values['count']
                                    ).to_market()
                            else:
                                return HttpResponse(gform.errors, )
                            if count == 0:
                                break
        else:
            last = Issuance.objects.filter(date__year=datetime.now().year).aggregate(Max('pk'))
            if last['pk__max']:
                number = last['pk__max'] + 1
            else:
                number = 1
            p = Market.objects.all()
            gselect = Goods.objects.all()
            context_dict = dict(request=request, p_title=p_title, p=p, res=res,
                                gselect=gselect, number=number, )
            context_dict.update(csrf(request))
            return render_to_response("issuance_form.html", context_dict)

    elif act == 'del':
        id = int(request.GET['id'])
        try:
            issuance = Issuance.objects.get(pk=id)
        except Issuance.DoesNotExist:
            res = json.dumps(dict(res=-1))
            return HttpResponse(res, content_type="application/json")
        # if allready have sells stop delete return 0
        if issuance.has_sell() > 0:
            res = json.dumps(dict(res=0))
            return HttpResponse(res, content_type="application/json")
        else:
            for g in IssuanceGoods.objects.filter(issuance=issuance):
                # return goods to warehouse
                ig = g.goods # invoice goods
                ig.balance = ig.balance + g.balance
                ig.save()
                g.delete()
            issuance.delete()
            res = json.dumps(dict(res=1))
            return HttpResponse(res, content_type="application/json")

    elif act == 'edit':
        try:
            issuance = Issuance.objects.get(pk=id)
        except Issuance.DoesNotExist:
            o_name = "Документ "
            b_url = reverse('issuance')
            context_dict = dict(request=request, o_name=o_name, b_url=b_url,)
            return render_to_response("err404.html", context_dict)

        if request.method == 'POST':
            for g in IssuanceGoods.objects.filter(issuance=issuance):
                # return goods to warehouse
                ig = g.goods
                ig.balance = ig.balance + g.balance
                ig.save()
                g.delete()
            total = 0
            post_values = request.POST.copy()
            for i in range(int(post_values['goods_cnt']) + 2):
                post_values['issuance'] = issuance.pk
                if "cnt" + str(i) in post_values.keys():
                    try:
                        count = int(post_values['cnt' + str(i)])
                    except ValueError:
                        res = res + ' ValueError'
                        continue 
                    if count < 1:
                        res = res + ' count < 1'
                        continue
                    postg = int(post_values['goods' + str(i)])
                    # get goods from warehouse by invoices
                    for g in InvoiceGoods.objects.filter(goods=postg, balance__gt=0).order_by('expirydate'):
                        if count > g.goods.in_stock():
                            res = res + u' Превышено количество товаров на складе'
                            IssuanceGoods.objects.filter(issuance=issuance).delete()
                            Issuance.objects.filter(pk=issuance.pk).delete()
                            return HttpResponse(res, content_type='text/html; charset=utf-8')
                        if count > g.balance:
                            post_values['count'] = g.balance
                            count -= g.balance
                        else:
                            post_values['count'] = count
                            count = 0
                        post_values['goods'] = g.id
                        post_values['note'] = post_values['note' + str(i)]
                        post_values['balance'] = post_values['count']
                        gform = FormIssuanceGoods(post_values)
                        if gform.is_valid():
                            IssuanceGoods(issuance = issuance,
                                goods = g,
                                count = post_values['count'],
                                note = post_values['note'],
                                balance = post_values['count']
                                ).to_market()
                        else:
                            return HttpResponse(gform.errors, content_type='text/html')
                        if count == 0:
                            break                
            return HttpResponseRedirect(reverse('issuance'))
        gselect = Goods.objects.all()
        igoods = {}
        for g in IssuanceGoods.objects.filter(issuance=issuance):
            if g.goods.goods.pk in igoods:
                max_cnt = igoods[ g.goods.goods.pk ][0] + g.count
                min_cnt = igoods[ g.goods.goods.pk ][1] + g.count - g.balance
                cnt = igoods[ g.goods.goods.pk ][0] + g.count
                igoods[ g.goods.goods.pk ] = (max_cnt, min_cnt, cnt)
            else:
                igoods[ g.goods.goods.pk ] = (g.count + g.goods.goods.in_stock(),
                                              g.count - g.balance,
                                              g.count )

        context_dict = dict(request=request, p_title=p_title, res=res, edit=1,
                            gselect=gselect, issuance=issuance, igoods=igoods)
        context_dict.update(csrf(request))
        return render_to_response("issuance_form.html", context_dict)                    
    lst = []
    if 'query' in request.GET.keys():
        query = request.GET.get('query')
        issuance = Issuance.objects.filter(number__icontains=query).order_by('id')
        but_all = 1
    else:
        issuance = Issuance.objects.all().order_by('-id')
        but_all = 0
    for i in issuance:
        goods = IssuanceGoods.objects.filter(issuance=i)
        lst.append((i, goods))
    context_dict = dict(request=request, but_all=but_all, lst=lst, res=res)
    context_dict.update(csrf(request))
    return render_to_response("issuance.html", context_dict)

@login_required(login_url='/login')
def market(request, id=0, act=None):
    b_url = reverse('market')
    p_title = 'Торговая точка'
    if act == 'add':
        if request.method == 'POST':
            form = FormMarket(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(b_url)
        context_dict = dict(request=request, p_title=p_title, b_url=b_url)
        context_dict.update(csrf(request))
        return render_to_response("market_point_add.html", context_dict)

    elif id > 0:
        try:
            m = Market.objects.get(pk=id)
        except Market.DoesNotExist:
            o_name = p_title
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if act == 'del':
            try:
                m.delete()
            except ProtectedError:
                o_name = m.name
                context_dict = dict(request=request, o_name=o_name, b_url=b_url)
                return render_to_response("errdelete.html", context_dict)
        elif act == 'edit':
            p_title = 'Редактирование торговой точки'
            if request.method == 'POST':
                form = FormMarket(request.POST,instance=m)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(b_url)
            context_dict = dict(request=request, p_title=p_title, m=m, b_url=b_url)
            context_dict.update(csrf(request))
            return render_to_response("market_point_add.html", context_dict)
        elif act == 'view':
            p_title = m.name
            i = Issuance.objects.filter(market=m).values('pk')
            ig = IssuanceGoods.objects.filter(balance__gt=0, issuance__in=i).values('goods')
            glst = InvoiceGoods.objects.filter(pk__in=ig).values('goods')
            lst = Goods.objects.filter(pk__in=glst).order_by('name')
            context_dict = dict(request=request, lst=lst, p_title=p_title, b_url=b_url)
            return render_to_response("market_view.html", context_dict)

    lst = Market.objects.all().order_by('name')

    context_dict = dict(request=request, lst=lst, p_title=p_title)
    return render_to_response("market_point.html", context_dict)

@login_required(login_url='/login')
def market_goods(request,):
    try:
        m = Market.objects.get(pk=int(request.GET['m']))
        i = Issuance.objects.filter(market=m).values('pk')
        ig = IssuanceGoods.objects.filter(balance__gt=0, issuance__in=i).values('goods')
        glst = InvoiceGoods.objects.filter(pk__in=ig).values('goods')
        lst = {}
        for g in Goods.objects.filter(pk__in=glst).order_by('name'):
            if g.on_market() > 0:
                lst [g.pk] = (g.pk, g.name, g.on_market())
        # return HttpResponse(lst, content_type="application/json")
        return HttpResponse(json.dumps(lst), content_type="application/json")
    except Market.DoesNotExist:
        return HttpResponse(json.dumps(dict(res=0)), content_type="application/json")

@login_required(login_url='/login')
def provider_goods(request, id=0):
    try:
        prov = Provider.objects.get(pk=id)
        try:
            goods_pk = GoodsProvider.objects.filter(provider=prov).values('goods')
            lst = Goods.objects.filter(pk__in=goods_pk).order_by('name')
        except Goods.DoesNotExist:
            lst = []
            # lst = ('Нет товаров':0)
    except Provider.DoesNotExist:
        lst = []
    context_dict = dict(request=request, lst=lst)
    return render_to_response("provider_goods.html", context_dict)

@login_required(login_url='/login')
def invoice(request, id=0, act=None):
    if act == 'del':
        cnt = 0
        if 'id' in request.GET.keys():
            try:
                i = Invoice.objects.get(pk=int(request.GET['id']))
            except Exception, e:
                res = json.dumps(dict(res=-10))
                return HttpResponse(res, content_type="application/json")

            try:
                cnt = InvoiceGoods.objects.filter(invoice=i).delete()
            except Exception, e:
                res = json.dumps(dict(res=-100))
                return HttpResponse(res, content_type="application/json")
            try:
                i.delete()
            except Exception, e:
                res = json.dumps(dict(res=-300))
                return HttpResponse(res, content_type="application/json")
        else:
            res = json.dumps(dict(res=-600))
            return HttpResponse(res, content_type="application/json")

        res = json.dumps(dict(res=1))
        return HttpResponse(res, content_type="application/json")

    res = ""
    p_title = "Приходая накладная"
    form = FormInvoice()
    if act == 'add':
        if request.method == 'POST':
            post_values = request.POST.copy()
            post_values['manager'] = request.user.id
            datein = strptime(post_values['date'],"%d.%m.%Y")
            post_values['date'] = date(datein.tm_year, datein.tm_mon, datein.tm_mday,)
            post_values['note'] = post_values['inote']
            form = FormInvoice(post_values)
            if form.is_valid():
                invoice = form.save()
                for i in range(int(post_values['goods_cnt'])+1):
                    post_values['invoice'] = invoice.pk
                    if "cnt" + str(i) in post_values.keys():
                        try:
                            count = int(post_values['cnt' + str(i)])
                        except ValueError:
                            res = res + ' ValueError'
                            continue 
                        if count < 1:
                            res = res + ' count < 1'
                            continue
                        post_values['goods'] = post_values['goods' + str(i)]
                        post_values['count'] = post_values['cnt' + str(i)]
                        post_values['balance'] = post_values['count']
                        post_values['cost'] = post_values['cost' + str(i)]
                        post_values['note'] = post_values['note' + str(i)]
                        expirydate = strptime(post_values['date_expiry' + str(i)],"%d.%m.%Y")
                        post_values['expirydate'] = date(expirydate.tm_year,
                                                         expirydate.tm_mon,
                                                         expirydate.tm_mday,)
                        g_form = FormInvoceGoods(post_values)
                        if g_form.is_valid():
                            g_form.save()
            return HttpResponseRedirect(reverse('invoice'))
        p = Provider.objects.all()
        context_dict = dict(request=request, p_title=p_title, p=p, res=res,)
        context_dict.update(csrf(request))
        return render_to_response("invoice_form.html", context_dict)

    elif id > 0:
        try:
            invoice = Invoice.objects.get(pk=id)
        except Invoice.DoesNotExist:
            o_name = "Документ "
            b_url = reverse('invoice')
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if act == 'edit':
            p_title = 'Редактирование накладной'
            if request.method == 'POST':
                post_values = request.POST.copy()
                invoice.manager = request.user
                invoice.note = post_values['inote']
                invoice.save()
                editgoods = []
                for i in range(int(post_values['goods_cnt'])+1):
                    post_values['invoice'] = id
                    if "cnt" + str(i) in post_values.keys():
                        try:
                            count = int(post_values['cnt' + str(i)])
                        except ValueError:
                            res = res + ' ValueError'
                            continue
                        goods = int(post_values['goods' + str(i)])
                        try:
                            eg = InvoiceGoods.objects.get(invoice=invoice, goods=goods)
                        except InvoiceGoods.DoesNotExist:
                            # add new goods to the invoice
                            post_values['goods'] = goods
                            post_values['count'] = post_values['cnt' + str(i)]
                            post_values['balance'] = post_values['count']
                            post_values['cost'] = post_values['cost' + str(i)]
                            post_values['note'] = post_values['note' + str(i)]
                            expirydate = strptime(post_values['date_expiry' + str(i)],"%d.%m.%Y")
                            post_values['expirydate'] = date(expirydate.tm_year,
                                                         expirydate.tm_mon,
                                                         expirydate.tm_mday,)
                            g_form = FormInvoceGoods(post_values)
                            if g_form.is_valid():
                                eg = g_form.save()
                                editgoods.append(eg.pk)
                                res = 'new'
                                continue
                            else:
                                res = g_form.errors
                                continue
                        cnt = int(post_values['cnt' + str(i)])
                        sold = eg.count - eg.balance
                        if sold <= cnt:
                            post_values['count'] = post_values['cnt' + str(i)]
                            post_values['balance'] = cnt - sold
                            post_values['goods'] = eg.goods.pk
                            post_values['cost'] = post_values['cost' + str(i)]
                            post_values['note'] = post_values['note' + str(i)]
                            expirydate = strptime(post_values['date_expiry' + str(i)],"%d.%m.%Y")
                            post_values['expirydate'] = date(expirydate.tm_year,
                                                         expirydate.tm_mon,
                                                         expirydate.tm_mday,)
                            g_form = FormInvoceGoods(post_values, instance=eg)
                            if g_form.is_valid():
                                g_form.save()
                            else:
                                res += str(g_form.errors)

                        else:
                            res = post_values['goods' + str(i)] + u' Не допустимо малое количество для' + eg.goods.name
                        editgoods.append(eg.pk)

                InvoiceGoods.objects.filter(balance=F('count'), invoice=invoice).exclude(pk__in=editgoods).delete()

                return HttpResponseRedirect(reverse('invoice'))

            g = InvoiceGoods.objects.filter(invoice=invoice)
            context_dict = dict(request=request, edit=1, p_title=p_title,
                                i=invoice, g=g, res=res)
            context_dict.update(csrf(request))
            return render_to_response("invoice_form.html", context_dict)


    lst = []
    if 'query' in request.GET.keys():
        query = request.GET.get('query')
        invoices = Invoice.objects.filter(number__icontains=query).order_by('-date')
        but_all = 1
    else:
        invoices = Invoice.objects.all().order_by('-date')
        but_all = 0
    for i in invoices:
        goods = InvoiceGoods.objects.filter(invoice=i)
        lst.append((i, goods))
    context_dict = dict(request=request, p_title=p_title, but_all=but_all,
                        lst=lst, res=res, form=form)
    context_dict.update(csrf(request))
    return render_to_response("invoice.html", context_dict)

@login_required(login_url='/login')
def warehouse(request, **kwargs):
    glst = InvoiceGoods.objects.filter(balance__gt=0).values('goods')
    lst = Goods.objects.filter(pk__in=glst).order_by('name')
    context_dict = dict(request=request, lst=lst)
    return render_to_response("warehouse.html", context_dict)

@login_required(login_url='/login')
def goods_bar_code(request, ):
    try:
        gpk = int(request.GET['goods'])
        code = Decimal(request.GET['bcode'].strip())
        if gpk > 0:
            goods = Goods.objects.get(pk=gpk)
            bcode = BarCode.objects.filter(code=code).exclude(goods=goods)
        else:
            bcode = BarCode.objects.filter(code=code)
        bcode = bcode[0]
        res = json.dumps(dict(res=1, goods=bcode.goods.name ))
    except:
        res = json.dumps(dict(res=0))
    return HttpResponse(res, content_type="application/json")

@login_required(login_url='/login')
def goods(request, id=0, act=None ):
    res=""
    if act == 'add':
        m = Measure.objects.all()
        p = Provider.objects.all()
        gt = GoodsType.objects.exclude(name__in=['SERVICE', 'PTT', '1PTT'])
        p_title = "Новый товар"
        if request.method == 'POST':
            post_values = request.POST.copy()
            if "client_only" in request.POST.keys():
                post_values['client_only'] = 1
            else:
                post_values['client_only'] = 0
            post_values['single_visit'] = 0
            post_values['is_discount'] = 0
            form = FormGoods(post_values)
            if form.is_valid():
                g = form.save()
                if request.POST['price']:
                    date_s = strptime(request.POST['date_start'],"%d.%m.%Y")
                    date_s = date(date_s.tm_year,date_s.tm_mon,date_s.tm_mday,)
                    g.new_price(request.POST['price'], date_s)

                for bcode in request.POST.getlist('bar_code'):
                    if bcode != '':
                        try:
                            code=Decimal(bcode.strip())
                        except Exception, e:
                            continue
                        bar_code = BarCode(goods=g, code=code)
                        bar_code.save()
                for i in range(int(request.POST['maxprov'])+1):
                    key = 'provider' + str(i)
                    if key in request.POST.keys():
                        try:
                            prov_pk = int(request.POST[key])
                        except ValueError:
                            prov_pk = 0
                        try:
                            prov = Provider.objects.get(pk=prov_pk)
                            gprovider = GoodsProvider(goods=g,
                                        provider=prov)
                            gprovider.save()
                        except Provider.DoesNotExist:
                            pass
                        
                return HttpResponseRedirect(reverse('goods'))

        context_dict = dict(request=request, p_title=p_title,
                            m=m, p=p, departments=departments, gt=gt,
                            )
        # url = resolve
        context_dict.update(csrf(request))
        return render_to_response("goods_add.html", context_dict)
    elif id > 0:
        m = Measure.objects.all()
        p = Provider.objects.all()
        gt = GoodsType.objects.all().exclude(name__in=['SERVICE', 'PTT', '1PTT'])
        try:
            g = Goods.objects.get(pk=id)
        except Goods.DoesNotExist:
            o_name = "Товар"
            b_url = reverse('goods')
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if act == 'del':
            if InvoiceGoods.objects.filter(goods=g).count() > 0:
                o_name = g.name
                b_url = reverse('goods')
                context_dict = dict(request=request, o_name=o_name, b_url=b_url)
                return render_to_response("errdelete.html", context_dict)
            else:
                Price.objects.filter(goods=g).delete()
                BarCode.objects.filter(goods=g).delete()
                GoodsProvider.objects.filter(goods=g).delete()
                g.delete()
        elif act == 'edit':
            p_title = "Товар"
            if request.method == 'POST':
                post_values = request.POST.copy()
                if "client_only" in request.POST.keys():
                    post_values['client_only'] = 1
                else:
                    post_values['client_only'] = 0
                post_values['single_visit'] = 0
                post_values['is_discount'] = 0
                form = FormGoods(post_values, instance=g)
                if form.is_valid():
                    form.save()
                if request.POST['price']:
                    new_price = Decimal(request.POST['price'])
                    if g.price() != new_price:
                        date_s = strptime(request.POST['date_start'],"%d.%m.%Y")
                        date_s = date(date_s.tm_year,date_s.tm_mon,date_s.tm_mday,)
                        g.new_price(request.POST['price'], date_s)

                BarCode.objects.filter(goods=g).delete()
                GoodsProvider.objects.filter(goods=g).delete()
                for bcode in request.POST.getlist('bar_code'):
                    if bcode != '':
                        try:
                            code=Decimal(bcode.strip())
                        except Exception, e:
                            continue
                        bar_code = BarCode(goods=g, code=code)
                        bar_code.save()
                for i in range(int(request.POST['maxprov'])+1):
                    key = 'provider' + str(i)
                    if key in request.POST.keys():
                        try:
                            prov_pk = int(request.POST[key])
                        except ValueError:
                            prov_pk = 0
                        try:
                            prov = Provider.objects.get(pk=prov_pk)
                            gprovider = GoodsProvider(goods=g,
                                        provider=prov)
                            gprovider.save()
                        except Provider.DoesNotExist:
                            pass
                return HttpResponseRedirect(reverse('goods'))
            price = Price.objects.filter(goods=g)
            bcode = BarCode.objects.filter(goods=g)
            prov = GoodsProvider.objects.filter(goods=g)
            context_dict = dict(request=request, p_title=p_title, g=g, gt=gt,
                                m=m, p=p, departments=departments, edit=1,
                                price=price, bcode=bcode, prov=prov)
            context_dict.update(csrf(request))
            return render_to_response("goods_add.html", context_dict)

    sysgt = GoodsType.objects.filter(name__in=['SERVICE', 'PTT', '1PTT'])
    lst = Goods.objects.all().exclude(goods_type__in=sysgt).order_by('name')
    context_dict = dict(request=request, lst=lst)
    return render_to_response("goods.html", context_dict)

@login_required(login_url='/login')
def goods_type(request, id=0, **kwargs):
    if kwargs['act'] == 'add':
        p_title = "Новый вид товаров"
        if request.method == 'POST':
            form = FormGoodsType(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(reverse('goods_type'))
        context_dict = dict(request=request, p_title=p_title, )
        context_dict.update(csrf(request))
        return render_to_response("goods_type_add.html", context_dict)    
    elif id > 0:
        try:
            gt = GoodsType.objects.get(pk=id)
        except GoodsType.DoesNotExist:
            o_name = "вид товара"
            b_url = reverse('goods_type')
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if kwargs['act'] == 'del':
            try:
                gt.delete()
            except ProtectedError:
                o_name = gt.name
                b_url = reverse('goods_type')
                context_dict = dict(request=request, o_name=o_name, b_url=b_url)
                return render_to_response("errdelete.html", context_dict)
            
        elif kwargs['act'] == 'edit':
            p_title = "Вид товара"
            if request.method == 'POST':
                form = FormGoodsType(request.POST,instance=gt)
                if form.is_valid():
                    form.save()
                return HttpResponseRedirect(reverse('goods_type'))
            context_dict = dict(request=request, p_title=p_title, gt=gt)
            context_dict.update(csrf(request))
            return render_to_response("goods_type_add.html", context_dict)
    # SERVICE system type, add manual
    lst = GoodsType.objects.exclude(name__in=['SERVICE', 'PTT', '1PTT']).order_by('name')
    context_dict = dict(request=request, lst=lst)
    return render_to_response("goods_type.html", context_dict)

@login_required(login_url='/login')
def measure(request, id=0, **kwargs):
    if kwargs['act'] == 'add':
        p_title = "Новая единица измерения"
        if request.method == 'POST':
            form = FormMeasure(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(reverse('measure'))
        context_dict = dict(request=request, p_title=p_title, )
        context_dict.update(csrf(request))
        return render_to_response("measure_add.html", context_dict)
    elif id > 0:
        try:
            m = Measure.objects.get(pk=id)
        except Measure.DoesNotExist:
            o_name = "Единица измерения"
            b_url = reverse('measure')
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if kwargs['act'] == 'del':
            try:
                m.delete()
            except ProtectedError:
                o_name = m.name
                b_url = reverse('measure')
                context_dict = dict(request=request, o_name=o_name, b_url=b_url)
                return render_to_response("errdelete.html", context_dict)
        elif kwargs['act'] == 'edit':
            p_title = "Единица измерения"
            if request.method == 'POST':
                form = FormMeasure(request.POST,instance=m)
                if form.is_valid():
                    form.save()
                return HttpResponseRedirect(reverse('measure'))
            context_dict = dict(request=request, p_title=p_title, m=m)
            context_dict.update(csrf(request))
            return render_to_response("measure_add.html", context_dict)

    lst = Measure.objects.all().order_by('name')
    context_dict = dict(request=request, lst=lst)
    return render_to_response("measure.html", context_dict)    

@login_required(login_url='/login')
def fin_menu(request,):
    context_dict = dict(request=request,)
    return render_to_response("fin_menu.html", context_dict)

@login_required(login_url='/login')
def provider(request, p_id=0, **kwargs):
    if kwargs['act'] == 'add':
        p_title = "Новый постащик"
        if request.method == 'POST':
            form = FormProvider(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(reverse('provider'))
        context_dict = dict(request=request, p_title=p_title, )
        context_dict.update(csrf(request))
        return render_to_response("provider_add.html", context_dict)

    elif kwargs['act'] == 'edit':
        try:
            p = Provider.objects.get(pk=p_id)
        except Provider.DoesNotExist:
            o_name = "Поставщик"
            b_url = reverse('provider')
            context_dict = dict(request=request, o_name=o_name, b_url=b_url)
            return render_to_response("err404.html", context_dict)
        if request.method == 'POST':
            form = FormProvider(request.POST, instance=p)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(reverse('provider'))
        p_title = "Редактирование постащика"
        context_dict = dict(request=request, p_title=p_title, p=p)
        context_dict.update(csrf(request))
        return render_to_response("provider_add.html", context_dict)

    lst = Provider.objects.all().order_by('name')
    context_dict = dict(request=request, lst=lst)
    return render_to_response("provider.html", context_dict)

@login_required(login_url='/login')
def products_menu(request,):
    context_dict = dict(request=request,)
    return render_to_response("products_menu.html", context_dict)
