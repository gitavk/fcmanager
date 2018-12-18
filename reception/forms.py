# -*- coding: utf-8 -*-
from django.forms import ModelForm

from models import Reminder, Guest


class FormReminder(ModelForm):
    class Meta:
        model = Reminder


class FormGuest(ModelForm):
    class Meta:
        model = Guest
