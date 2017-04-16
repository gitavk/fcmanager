# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from models import *

class form_client_add(ModelForm):
    """docstring for person_add"""
    class Meta:
        model = Client
        # fields = ('avatar','first_name','last_name')
        exclude = ['is_online']