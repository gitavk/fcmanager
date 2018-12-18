from datetime import timedelta
import re

from django import template

from finance.models import Invitation
from reception.models import Guest
from person.models import Client
from employees.models import Timetable

register = template.Library()


@register.filter
def shift_trainer_pk(date, shift):
    try:
        shift = Timetable.objects.get(date=date, shift=shift)
        return shift.employee.pk
    except Timetable.DoesNotExist:
        return 0


@register.filter
def shift_trainer(date, shift):
    try:
        shift = Timetable.objects.get(date=date, shift=shift)
        return shift.employee.initials()
    except Timetable.DoesNotExist:
        return ''


@register.filter
def has_invite(guest=0, client=0):
    if guest:
        try:
            g = Guest.objects.get(pk=guest)
        except Guest.DoesNotExist:
            return False
        if Invitation.objects.filter(guest=g, is_free=True).count() > 0:
            return True
        else:
            return False
    else:
        try:
            c = Client.objects.get(pk=client)
        except Client.DoesNotExist:
            return False
        if Invitation.objects.filter(client=c, is_free=True).count() > 0:
            return True
        else:
            return False


@register.filter
def replace(string, args):
    search = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub(search, replace, str(string))


@register.filter
def lookup(d, key):
    try:
        return d[key]
    except IndexError:
        return 'dd'


@register.filter
def multiplication(d, key):
    return (d - 1) * key


@register.filter
def planDeltaDays(d, key):
    return d + timedelta(days=(key - 1) * 30)


@register.filter
def precent(d, key):
    return d * key / 100


@register.filter
def integer(d):
    return int(d)
