# -*- coding: utf-8 -*-
from time import strptime
from datetime import datetime, date, time

from django.conf import settings
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

from contract.models import *
from person.models import *
from employees.models import Employee, Visits as eVisits
from finance.models import *
from finance.forms import *
from .models import *
from .forms import *

day_name = "понедельник вторник среда четверг пятница суббота воскресенье"
day_name = day_name.split()

abc = ("А","Б","В","Г","Д","Е","Ё","Ж","З","И","К",
       "Л","М","Н","О","П","Р","С","Т","У","Ф","Х",
       "Ц","Ч","Ш","Щ","Э","Ю","Я",)

@login_required(login_url='/login/')
def guest_visit(request, id=0, ):
	try:
		guest = Guest.objects.get(pk=id)
	except Guest.DoesNotExist:
		o_name = 'Гость'
		context_dict = dict(request=request, o_name=o_name, b_url=b_url)
		return render_to_response("err404.html", context_dict)
	b_url = reverse('r_guest_card', args=(guest.pk, ))
	if request.method == 'POST':
		post_val = request.POST.copy()
		post_val['date'] = datetime.now()
		f = FormInvitation(post_val)
		if f.is_valid():
			f.save()
			return HttpResponseRedirect(b_url)
		else:
			return HttpResponse(f.errors)
	context_dict = dict(request=request, g=guest, b_url=b_url)
	context_dict.update(csrf(request))
	return render_to_response('guest_visit.html', context_dict)

@login_required(login_url='/login/')
def cashier(request, ):
	p_title='Работа с кассой'
	cashhost = settings.CASHIER_HOST
	context_dict = dict(request=request, p_title=p_title, cashhost=cashhost,)
	return render_to_response("cashier.html", context_dict)

@login_required(login_url='/login/')
def guest_card(request, id=0, act=None ):
	b_url = reverse('r_guest')
	p_title = 'Личная карта гостя'
	cashhost = settings.CASHIER_HOST
	try:
		guest = Guest.objects.get(pk=id)
	except Guest.DoesNotExist:
		o_name = 'Гость'
		context_dict = dict(request=request, o_name=o_name, b_url=b_url)
		return render_to_response("err404.html", context_dict)

	try:
		v = GuestVisits.objects.get(guest=guest, is_online=-1)
		guest.is_online = True
	except GuestVisits.DoesNotExist:
		v = ""
		guest.is_online = False

	if act == 'inout':
		guest.is_online = not guest.is_online
		if guest.is_online:
			v = GuestVisits(date_start=datetime.now(),
	                      locker=request.POST['locker'],
	                      date_end=None,
	                      guest=guest)
			v.save()
		else:
			i = Invitation.objects.filter(guest=guest, is_free=True)[0]
			i.is_free = False
			i.save()
			v.out()
			v = ""

	visits = GuestVisits.objects.filter(guest=guest).order_by('date_start')
	credits = Credits.objects.filter(guest=guest).order_by('plan_date')

	context_dict = dict(request=request, b_url=b_url, p_title=p_title, guest=guest,
						v=v, visits=visits, credits=credits, cashhost = cashhost)
	context_dict.update(csrf(request))
	return render_to_response("guest_card.html", context_dict)

@login_required(login_url='/login/')
def clientinvite(request,):
	lst = []
	ct = ContractType.objects.filter(period_days__in=[182, 365])
	if 'query' in request.GET.keys():
		query = request.GET.get('query')
		if len(query) > 0:
			clnts = Client.objects.filter(last_name__icontains=query).order_by("last_name")
			for c in Contract.objects.filter(contract_type__in=ct,
											 is_current=1, client__in=clnts):
				invites = Invitation.objects.filter(contract=c)
				lst.append((c, invites))
		else:
			for c in Contract.objects.filter(contract_type__in=ct, is_current=1):
				invites = Invitation.objects.filter(contract=c)
				lst.append((c, invites))
	context_dict = dict(lst=lst, )
	return render_to_response("client_invite.html", context_dict)

@login_required(login_url='/login/')
def guest(request, id=-1, act=None):
	b_url = reverse('r_guest')
	p_title = 'Гость'
	lst = []
	if act == 'add':
		if request.method == 'POST':
			post_values = request.POST.copy()
			post_values['manager'] = request.user.pk
			post_values['is_client'] = 0
			post_values['date'] = datetime.now().date()
			d = strptime(post_values['born'],"%d.%m.%Y")
			post_values['born'] = date(d.tm_year, d.tm_mon, d.tm_mday,)
			form = FormGuest(post_values)
			if form.is_valid():
				# try:
				f = form.save()
				# except Exception:
				# 	context_dict = dict(form=form)
				# 	return render_to_response("form_err.html", context_dict)
			else:
				f = form.errors
			if 'contract' in post_values.keys():
				try:
					c_pk = int(post_values['contract'])
				except ValueError:
					c_pk = 0
				if c_pk > 0:
					post_values['guest'] = f.pk
					post_values['date'] = datetime.now()
					post_values['is_free'] = True
					fi = FormInvitation(post_values)
					if fi.is_valid():
						fi.save()
					else:
						fi = fi.errors
			url = reverse('r_guest', args=(0, ))
			return HttpResponseRedirect(url)
		context_dict = dict(request=request, p_title=p_title, b_url=b_url, )
		context_dict.update(csrf(request))
		return render_to_response("guest_add.html", context_dict)

	if 'query' in request.GET.keys():
		query = request.GET.get('query')
		lst = Guest.objects.filter(lastname__icontains=query).order_by("lastname")
	elif id > -1:
		lst = Guest.objects.filter(lastname__istartswith=abc[int(id)]).order_by("lastname")
	else:
		lst = Guest.objects.all().order_by("lastname")

	context_dict = dict(request=request, lst=lst, abc=abc, id=id)
	context_dict.update(csrf(request))
	return render_to_response("guest.html", context_dict)

@login_required(login_url='/login/')
def reminder(request, id=0, act=None):
	b_url = reverse('reminder')
	p_title = 'Напоминание'
	if act == 'add':
		if request.method == 'POST':
			post_values = request.POST.copy()
			post_values['author'] = request.user.pk
			t = strptime(request.POST['time'],"%H:%M")
			post_values['time'] = time(t.tm_hour, t.tm_min)
			post_values['is_everyday'] = False
			post_values['wdays'] = ""
			post_values['group1'] = int(post_values['group1'])
			if post_values['group1'] == 1:
				post_values['is_everyday'] = True
			elif post_values['group1'] == 2:
				d = strptime(request.POST['date'],"%d.%m.%Y")
				post_values['date'] = date(d.tm_year, d.tm_mon, d.tm_mday,)
			elif post_values['group1'] == 3:
				for i in xrange(0,7):
					if "wday" + str(i) in post_values.keys():
						post_values['wdays'] += str(i) + "," 

			form = FormReminder(post_values)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(b_url)
			else:
				p_title = form.errors
		context_dict = dict(request=request, p_title=p_title, b_url=b_url, week=day_name)
		context_dict.update(csrf(request))
		return render_to_response("reminder_add.html", context_dict)
	elif id > 0:
		try:
			r = Reminder.objects.get(pk=id)
		except Reminder.DoesNotExist:
			o_name = p_title
			context_dict = dict(request=request, o_name=o_name, b_url=b_url)
			return render_to_response("err404.html", context_dict)
		if act == 'del':
			r.delete()
		elif act == 'read':
			r.read(request.user)

	lst = []
	for r in  Reminder.objects.all().order_by('is_everyday','date','wdays'):
		if r.is_everyday:
			lst.append((r,1))
		elif r.date:
			lst.append((r,2))
		else:
			wl = [int(x) for x in r.wdays[:-1].split(',')]
			lst.append((r,wl))

	context_dict = dict(request=request, lst=lst, week=day_name)
	context_dict.update(csrf(request))
	return render_to_response("reminder.html", context_dict)

@login_required(login_url='/login/')
def bithday(request):
	if request.method == 'POST':
		born = strptime(request.POST['born_date'],"%d.%m")
		d = born.tm_mday
		m = born.tm_mon
		rdate = date(datetime.now().year,m,d,)
	else:
		d = datetime.now().day
		m = datetime.now().month
		rdate = datetime.now()
	c = Contract.objects.filter(is_current=True).values('client')
	lst = Client.objects.filter(born_date__month=m, born_date__day=d, pk__in=c).order_by("last_name")

	context_dict = dict(request=request, lst=lst, rdate=rdate)
	context_dict.update(csrf(request))
	return render_to_response("bithday.html", context_dict)

@login_required(login_url='/login/')
def clients_login(request,):
	lst = []
	employees = []
	if request.method == 'POST':
		try:
			find = long(request.POST.get('lastname'))
		except ValueError:
			find = request.POST.get('lastname')

		if isinstance(find, long):
			res = Contract.objects.filter(card=find, is_current=1)
			# if not find in the current try find in the prospect
			if res.count() < 1:
				res = Contract.objects.filter(card=find, is_current=2)
			employees = Employee.objects.filter(card=find,)
		else:
			ac = Contract.objects.filter(is_current__in=[1, 2]).values('client')
			res = Client.objects.filter(last_name__icontains=find, pk__in=ac)
			employees = Employee.objects.filter(lastname__icontains=find)

		if res.count() + employees.count() == 1:
			if employees:
				url = reverse('e_comein', args=(employees[0].pk, ))
			else:
				try: # if contract
					url = reverse('person_card',args=[res[0].client.pk])
				except AttributeError:
					url = reverse('person_card',args=[res[0].pk])
			return HttpResponseRedirect(url)
		else:
			lst = res
			
	context_dict = dict(request=request, lst=lst, employees=employees)
	context_dict.update(csrf(request))
	return render_to_response("client_login.html", context_dict, )

@login_required(login_url='/login/')
def clients_online(request,):
	lst = []
	for v in Visits.objects.filter(is_online=-1).order_by('date_start'):
		debts = Credits.objects.filter(client=v.contract.client).count()
		lst.append((debts,v))
	glst = []

	for gv in GuestVisits.objects.filter(is_online=-1).order_by('date_start'):
		debts = Credits.objects.filter(guest=gv.guest).count()
		glst.append((debts, gv))

	elst = eVisits.objects.filter(date_end__isnull=True).order_by('date_start')

	context_dict = dict(request=request, lst = lst, glst=glst, elst=elst)
	return render_to_response("online.html", context_dict, )

@login_required(login_url='/login/')
def reception_menu(request,):
	Y = datetime.today().year
	m = datetime.today().strftime("%m")
	d = datetime.today().strftime("%d")
	context_dict = dict(request=request, Y=Y, m=m, d=d, )
	return render_to_response("reception_menu.html", context_dict, )
