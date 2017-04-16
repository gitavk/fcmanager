# -*- coding: utf-8 -*-
from datetime import date, datetime
from time import strptime

from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from forms import *
from person.models import Client
from core.models import User

@login_required(login_url='/login/')
def guest(request, id=0, **kwargs):
	res = ""
	form = FormGuest()
	clnt = ""
	if kwargs['act'] == 'edit':
		try:
			guest = Guest.objects.get(pk=id)
			request.manager = guest.manager
		except Guest.DoesNotExist:
			o_name = "Гость"
			b_url = reverse('o_menu')
			context_dict = dict(request=request, o_name=o_name, b_url=b_url)
			return render_to_response("err404.html", context_dict)

		form = FormGuest(instance=guest)
		# for field phone it can be change only by the guest manager
		if guest.manager == request.user:
			request.readonly = 0
		else:
			request.readonly = 1

	if request.method == 'POST':
		post_value = request.POST.copy()
		if kwargs['act'] == 'edit':
			# when edit do not change date, is_client and manager
			post_value['date'] = guest.date
			post_value['is_client'] = guest.is_client
			post_value['manager'] = guest.manager.pk
			if request.readonly:
				post_value['phone'] = guest.phone

			form = FormGuest(post_value, instance=guest)
			res = "old form"
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(reverse('o_menu'))
		else:
			post_value['manager'] = request.user.pk
			post_value['date'] = datetime.now()
			post_value['is_client'] = 0
			form = FormGuest(post_value)
			if form.is_valid():
				clnt = Client.objects.filter(phone=post_value['phone'])
				if clnt.count() < 1:
					res = "OK"
					form.save()
					return HttpResponseRedirect(reverse('o_menu'))
				else:
					clnt = clnt[0]

	context_dict = dict(request=request, form=form, clnt=clnt, )
	context_dict.update(csrf(request))
	return render_to_response("o_guest.html", context_dict, )

@login_required(login_url='/login/')
def note_list(request, full=0, my=0 ):
	lst = []
	td = datetime.now().date()
	if my:
		if full:
			messages = Note.objects.filter(author=request.user, datetodo__lte=td).order_by('-id')
		else:
			messages = Note.objects.filter(author=request.user, datetodo__lte=td).order_by('-id')[:10]
	else:
		notes = NoteUsers.objects.filter(user=request.user, ).values('note',)
		if full:
			messages = Note.objects.filter(pk__in=notes, datetodo__lte=td).order_by('-id')
		else:
			messages = Note.objects.filter(pk__in=notes, datetodo__lte=td).order_by('-id')[:10]

	for msg in messages:
		if my:
			is_read = 0
		elif NoteUsers.objects.filter(user=request.user, is_read=0, note=msg, ).count():
			is_read = 1
		else:
			is_read = 0
		lst.append((msg, is_read))
	context_dict = dict(request=request, lst=lst, my=my, full=full)
	return render_to_response("note_list.html", context_dict, )

@login_required(login_url='/login/')
def note(request, id = 0):
	users = User.objects.filter(is_active=True)
	res = ""
	if request.method == 'POST':
		post_value = request.POST.copy()
		post_value['author'] = request.user.pk
		post_value['date'] = datetime.now()
		post_value['note_type'] = 0
		form = FormNote(post_value)
		if form.is_valid():
			note = form.save()
			if 'self' in request.POST.keys():
				NoteUsers(note=note, user=request.user).save()
			else:
				for u_id in request.POST.getlist('user'):
					user = User.objects.get(pk=int(u_id))
					NoteUsers(note=note, user=user).save()
			form = FormNote(instance=note)
			url = reverse('o_note_my')
			return HttpResponseRedirect(url)
	else:
		if id > 0:
			note = Note.objects.get(pk=id)
			try:
				nu = NoteUsers.objects.get(note=note, user=request.user)
					# if the Note is not notification than create notification
				if note.note_type != 1 and note.author != request.user and not nu.is_read:
					now_str = datetime.now().strftime('%H-%M %d.%m.%Y : ')
					who = request.user.get_full_name() 
					newtext = who + u' прочитал в ' + now_str + note.text
					notification = Note(text=newtext, author=request.user, note_type=1)
					notification.save()
					NoteUsers(note=notification, user=note.author).save()
				if not nu.is_read:
					NoteUsers.objects.filter(note=note, user=request.user).update(is_read=1)
			except NoteUsers.DoesNotExist:
				pass
			
			users = NoteUsers.objects.filter(note=note)
			context_dict = dict(request=request, note=note, users=users)
			return render_to_response("o_note_read.html", context_dict, )
		else:
			form = FormNote()

	context_dict = dict(request=request, form=form, users=users, res=res)
	context_dict.update(csrf(request))
	return render_to_response("o_note.html", context_dict, )

@login_required(login_url='/login/')
def organizer_menu(request, page=0):
	if 'query' in request.GET.keys():
		query = request.GET.get('query')
		lst = Guest.objects.filter(phone__icontains=query).order_by('last_name')
		scnt = lst.count()
		page = 0
	else:
		if 'page' in request.GET.keys():
			page = int(request.GET.get('page'))
			return HttpResponseRedirect(reverse('o_menu', args=(page,)))
		else:
			page = int(page)
		lst = Guest.objects.all().order_by('-id')[page*50:(page+1)*50]
		scnt = -1
	context_dict = dict(request=request, lst=lst, page=page, scnt=scnt)
	return render_to_response("organizer_menu.html", context_dict, )