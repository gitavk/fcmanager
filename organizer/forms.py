# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from models import *

class FormGuest(ModelForm):
    class Meta:
        model = Guest

class FormNote(ModelForm):
    class Meta:
        model = Note