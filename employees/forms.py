# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from models import *

class FormShift(ModelForm):
	class Meta:
		model = Shift

class FormTimetable(ModelForm):
	class Meta:
		model = Timetable

class FormWorkRecord(ModelForm):
	class Meta:
		model = WorkRecord

class FormEmployee(ModelForm):
    class Meta:
        model = Employee

class FormDepartment(ModelForm):
    class Meta:
        model = Department

class FormPosition(ModelForm):
    class Meta:
        model = Position