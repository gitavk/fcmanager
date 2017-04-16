# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from models import *


class form_Discount(ModelForm):
    class Meta:
        model = Discount
 
        
class form_Contract(ModelForm):
    class Meta:
        model = Contract
        exclude = ['discount','is_current']


class FormContractDateStart(ModelForm):
    class Meta:
        model = Contract
        fields = ['date_start', 'date_end']


class form_PayPlan(ModelForm):
    class Meta:
        model = PayPlan


class form_PayPlanSteps(ModelForm):
    class Meta:
        model = PayPlanSteps


class form_ContractText(ModelForm):
    class Meta:
        model = ContractText
        fields = ('firstpage', 'secondpage', 'person')


class form_ContractType(ModelForm):
    class Meta:
        model = ContractType


class form_PeriodTimeType(ModelForm):
    class Meta:
        model = PeriodTimeType


class form_PeriodTime(ModelForm):
    """docstring for person_add"""
    period_visit_end = forms.TimeField(input_formats=['%HH:%MM'])
    class Meta:
        model = PeriodTime
        fields = ('period_visit_start', 'period_visit_end', 'period_visit_wday')
