# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from models import *

class FormDepartmentsNames(ModelForm):
    """docstring for person_add"""
    class Meta:
        model = DepartmentsNames