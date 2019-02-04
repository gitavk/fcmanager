# -*- coding: utf-8 -*-
from time import strptime
from datetime import date, datetime, timedelta
from isoweek import Week
import json

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Max, ProtectedError

from .models import *
from .forms import *


@login_required(login_url='/login')
def visits(request, id=0):
    try:
        e = Employee.objects.get(pk=id)
    except Employee.DoesNotExist:
        return HttpResponse('Unknown employee', mimetype='text/html')

    lst = Visits.objects.filter(employee=e).order_by('date_start')
    context_dict = dict(request=request, online=lst, e=e)
    return render_to_response('e_visits.html', context_dict)


@login_required(login_url='/login')
def shift(request, ):
    (year, week) = datetime.now().isocalendar()[0:2]
    b_url = reverse('e_timetable', args=(year, week, '0'))

    if request.method == 'POST':
        post_values = {}
        post_values['date'] = datetime.now()
        de = request.POST.getlist('date_end')
        i = 0
        for s in request.POST.getlist('date_start'):
            post_values['time_start'] = s
            post_values['time_end'] = de[i]
            i += 1
            post_values['number'] = i
            f = FormShift(post_values)
            if f.is_valid():
                f.save()
            else:
                return HttpResponse(f.errors, mimetype='text/html')
        return HttpResponseRedirect(b_url)

    ldate = Shift.objects.all().aggregate(Max('date'))
    shifts = Shift.objects.filter(date=ldate['date__max'])
    context_dict = dict(request=request, b_url=b_url, shifts=shifts)
    context_dict.update(csrf(request))
    return render_to_response('shift.html', context_dict)


@login_required(login_url='/login')
def timetable(request, year=0, week=0, act=None):
    employees = Employee.objects.all()
    ldate = Shift.objects.all().aggregate(Max('date'))
    shifts = Shift.objects.filter(date=ldate['date__max'])
    (year, week) = (int(year), int(week))
    w = Week(year, week)
    # last week of current year
    lastw = w.last_week_of_year(year)[1]
    # last week of year before
    lastw_b = w.last_week_of_year(year - 1)[1]
    dates = [w.monday() + timedelta(days=i) for i in range(0, 7)]
    if act == 'copy':
        for d in dates:
            Timetable.objects.filter(date=d).delete()
            for s in shifts:
                try:
                    e = Timetable.objects.get(
                        date=d - timedelta(7), shift=s.pk
                    ).employee
                    tt = Timetable(date=d, shift=s, employee=e)
                    tt.save()
                except Timetable.DoesNotExist:
                    pass
        url = reverse('e_timetable', kwargs={'year': year, 'week': week, 'act': 0})
        return HttpResponseRedirect(url)

    if request.method == 'POST':
        post_values = {}
        i = 0
        employees = request.POST.getlist('employees')
        for j in range(0, 7):
            for s in shifts:
                post_values['date'] = dates[j]
                post_values['shift'] = s.pk
                try:
                    ttable = Timetable.objects.get(
                        date=post_values['date'], shift=s.pk)
                    ttable.delete()
                except Timetable.DoesNotExist:
                    pass
                post_values['employee'] = employees[i]
                if employees[i] != '0':
                    f = FormTimetable(post_values)
                    if f.is_valid():
                        f.save()
                    else:
                        return HttpResponse(f.errors, mimetype='text/html')
                i += 1

    context_dict = dict(
        request=request, week=week, dates=dates,
        shifts=shifts, year=year, lastw=lastw,
        lastw_b=lastw_b, employees=employees, act=act
    )
    if act == 'edit':
        context_dict.update(csrf(request))
    return render_to_response('timetable.html', context_dict)


@login_required(login_url='/login')
def note(request, id=0, ):
    b_url = reverse('e_view')
    if id:
        try:
            e = Employee.objects.get(pk=int(id))
            p_title = e.get_full_name()
        except Employee.DoesNotExist:
            p_title = 'Сотрудник'
            context_dict = dict(request=request, p_title=p_title, b_url=b_url)
            return render_to_response("e_err404.html", context_dict)

    if request.method == 'POST':
        if len(request.POST['note']) > 0:
            prefix = request.user.get_full_name() + ' ' + datetime.now().strftime("%d.%m.%Y") + ': '
            e.note = prefix + request.POST['note']
        else:
            e.note = ''
        e.save()
        url = reverse('e_card', args=(id, ))
        return HttpResponseRedirect(url)

    context_dict = dict(request=request, e=e, b_url=b_url)
    context_dict.update(csrf(request))
    return render_to_response('employees_note.html', context_dict)


@login_required(login_url='/login')
def online(request, ):
    online = Visits.objects.filter(date_end__isnull=True).order_by('date_start')
    context_dict = dict(request=request, online=online)
    return render_to_response('e_online.html', context_dict)


@login_required(login_url='/login')
def comein(request, id=0):
    b_url = reverse('client_login')
    p_title = ""
    if id:
        try:
            e = Employee.objects.get(pk=int(id))
            p_title = e.get_full_name()
        except Employee.DoesNotExist:
            p_title = 'Сотрудник'
            context_dict = dict(request=request, p_title=p_title, b_url=b_url)
            return render_to_response("e_err404.html", context_dict)

        if request.method == 'POST':
            e.comein()
            return HttpResponseRedirect(b_url)
    context_dict = dict(request=request, b_url=b_url, p_title=p_title, e=e)
    context_dict.update(csrf(request))
    return render_to_response('employees_comein.html', context_dict)


@login_required(login_url='/login')
def dismiss(request, ):
    res = 0
    if 'id' in request.GET.keys():
        try:
            e = Employee.objects.get(pk=int(request.GET.get('id')))
        except Employee.DoesNotExist:
            res = json.dumps(dict(res=-1))
            return HttpResponse(res, mimetype="application/json")
    else:
        res = json.dumps(dict(res=-1))
        return HttpResponse(res, mimetype="application/json")

    cnt = WorkRecord.objects.filter(
        employee=e, date_end__isnull=True
    ).update(date_end=datetime.now())
    res = json.dumps(dict(res=cnt))
    return HttpResponse(res, mimetype="application/json")


def departmentposions(request, ):
    plst = dict()
    for p in DepartmentPosition.objects.filter(department=int(request.GET.get('id'))):
        plst[p.pk] = p.position.name
    return HttpResponse(json.dumps(plst), mimetype="application/json")


@login_required(login_url='/login')
def change_work(request, id=0):
    p_title = 'Смена должности'
    b_url = reverse('e_card', args=(int(id), ))
    errors = ""
    try:
        e = Employee.objects.get(pk=id)
    except Employee.DoesNotExist:
        p_title = 'Сотрудник'
        context_dict = dict(request=request, p_title=p_title, b_url=b_url)
        return render_to_response("e_err404.html", context_dict)

    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['employee'] = e.pk
        post_values['date_start'] = datetime.now()
        wf = FormWorkRecord(post_values)
        if wf.is_valid():
            WorkRecord.objects.filter(
                employee=e, date_end__isnull=True
            ).update(date_end=datetime.now())
            wf.save()
            return HttpResponseRedirect(b_url)
        else:
            errors = wf.errors

    departments = Department.objects.all().order_by('name')
    positions = Position.objects.all().order_by('name')
    context_dict = dict(request=request, p_title=p_title, e=e, b_url=b_url,
                        departments=departments, positions=positions,
                        errors=errors,
                        )
    context_dict.update(csrf(request))
    return render_to_response('change_work.html', context_dict)


@login_required(login_url='/login')
def employee_card(request, id=0):
    p_title = 'Личная карта'
    b_url = reverse('e_view')
    f = FormEmployee()
    try:
        e = Employee.objects.get(pk=id)
    except Employee.DoesNotExist:
        p_title = 'Сотрудник'
        context_dict = dict(request=request, p_title=p_title, b_url=b_url)
        return render_to_response("e_err404.html", context_dict)
    if request.method == 'POST':
        post_values = request.POST.copy()
        post_values['date'] = datetime.now()
        f = FormEmployee(post_values, instance=e)
        if f.is_valid():
            f.save()
            return HttpResponseRedirect(b_url)

    departments = Department.objects.all().order_by('name')
    positions = Position.objects.all().order_by('name')
    context_dict = dict(request=request, p_title=p_title, b_url=b_url, e=e,
                        departments=departments, positions=positions,
                        f=f)
    context_dict.update(csrf(request))
    return render_to_response('employees_add.html', context_dict)


@login_required(login_url='/login')
def employees(request, id=0, act=None):
    p_title = "Сотрудники"
    b_url = reverse('employees')
    if act == 'view':
        lst = Employee.objects.all().order_by('lastname')
        context_dict = dict(request=request, p_title=p_title, lst=lst)
        return render_to_response("employees_view.html", context_dict)
    elif act == 'add':
        b_url = reverse('e_view')
        p_title = "Новый сотрудник"
        if request.method == 'POST':
            post_values = request.POST.copy()
            born = strptime(post_values['born'], "%d.%m.%Y")
            post_values['born'] = date(born.tm_year, born.tm_mon, born.tm_mday)
            post_values['date'] = datetime.now()
            f = FormEmployee(post_values)
            if f.is_valid():
                e = f.save()
                post_values['employee'] = e.pk
                post_values['date_start'] = datetime.now()
                wf = FormWorkRecord(post_values)
                if wf.is_valid():
                    wf.save()
                    return HttpResponseRedirect(b_url)
                else:
                    return HttpResponse(wf.errors, mimetype='text/html')
            else:
                return HttpResponse(f.errors, mimetype='text/html')
        departments = Department.objects.all().order_by('name')
        positions = Position.objects.all().order_by('name')
        context_dict = dict(request=request, p_title=p_title, b_url=b_url,
                            departments=departments, positions=positions,
                            new=1)
        context_dict.update(csrf(request))
        return render_to_response("employees_add.html", context_dict)

    wr = WorkRecord.objects.filter(date_end__isnull=True).values('employee')
    lst = Employee.objects.filter(pk__in=wr).order_by('lastname')
    (year, week) = datetime.now().isocalendar()[0:2]

    context_dict = dict(request=request, lst=lst, week=week, year=year)
    return render_to_response("employees.html", context_dict)


@login_required(login_url='/login')
def department(request, id=0, act=None):
    p_title = "Подразделения"
    b_url = reverse('department')
    if act == 'add':
        if request.method == 'POST':
            form = FormDepartment(request.POST)
            if form.is_valid():
                d = form.save()
            for p in request.POST.getlist('positions'):
                position = Position.objects.get(pk=int(p))
                DepartmentPosition(position=position, department=d).save()
            return HttpResponseRedirect(b_url)
        positions = Position.objects.all()
        context_dict = dict(
            request=request, p_title=p_title, b_url=b_url,
            positions=positions
        )
        context_dict.update(csrf(request))
        return render_to_response("department_add.html", context_dict)
    elif id > 0:
        try:
            d = Department.objects.get(pk=id)
        except Department.DoesNotExist:
            context_dict = dict(request=request, p_title=p_title, b_url=b_url)
            return render_to_response("e_err404.html", context_dict)
        if act == 'del':
            try:
                d.delete()
                return HttpResponseRedirect(b_url)
            except ProtectedError:
                context_dict = dict(request=request, o_name=d.name, b_url=b_url)
                return render_to_response("errdelete.html", context_dict)
        elif act == 'edit':
            p_title = 'Редактирование подразделения'
            if request.method == 'POST':
                form = FormDepartment(request.POST, instance=d)
                if form.is_valid():
                    form.save()
                DepartmentPosition.objects.filter(department=d).delete()
                for p in request.POST.getlist('positions'):
                    position = Position.objects.get(pk=int(p))
                    DepartmentPosition(position=position, department=d).save()
                return HttpResponseRedirect(b_url)
            positions = Position.objects.all()
            dep_positions = DepartmentPosition.objects.filter(
                department=d
            ).values_list('position', flat=True)
            context_dict = dict(
                request=request, p_title=p_title, edit=1, b_url=b_url,
                d=d, positions=positions, dep_positions=dep_positions
            )
            context_dict.update(csrf(request))
            return render_to_response("department_add.html", context_dict)

    lst = Department.objects.all().order_by('name')
    context_dict = dict(request=request, p_title=p_title, lst=lst)
    return render_to_response("department.html", context_dict)


@login_required(login_url='/login')
def position(request, id=0, act=None):
    p_title = "Должности"
    b_url = reverse('position')
    if act == 'add':
        if request.method == 'POST':
            form = FormPosition(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(b_url)
        context_dict = dict(request=request, p_title=p_title, b_url=b_url)
        context_dict.update(csrf(request))
        return render_to_response("position_add.html", context_dict)
    elif id > 0:
        try:
            p = Position.objects.get(pk=id)
        except Position.DoesNotExist:
            context_dict = dict(request=request, p_title=p_title, b_url=b_url)
            return render_to_response("e_err404.html", context_dict)
        if act == 'del':
            try:
                p.delete()
                return HttpResponseRedirect(b_url)
            except ProtectedError:
                context_dict = dict(request=request, o_name=p.name, b_url=b_url)
                return render_to_response("errdelete.html", context_dict)
        elif act == 'edit':
            p_title = 'Редактирование должности'
            if request.method == 'POST':
                form = FormPosition(request.POST, instance=p)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(b_url)
            context_dict = dict(request=request, p_title=p_title, p=p, b_url=b_url)
            context_dict.update(csrf(request))
            return render_to_response("position_add.html", context_dict)

    lst = Position.objects.all().order_by('name')
    context_dict = dict(request=request, p_title=p_title, lst=lst)
    return render_to_response("position.html", context_dict)
