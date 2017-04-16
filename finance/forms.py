# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from .models import *

class FormTrashGoods(ModelForm):
	class Meta:
		model = TrashGoods

class FormTrash(ModelForm):
	class Meta:
		model = Trash

class FormInvitation(ModelForm):
	class Meta:
		model = Invitation

class FormClient_PTT(ModelForm):
	class Meta:
		model = Client_PTT

class FormCredits(ModelForm):
	class Meta:
		model = Credits
		
class FormIssuance(ModelForm):
	class Meta:
		model = Issuance

class FormIssuanceGoods(ModelForm):
	class Meta:
		model = IssuanceGoods

class FormMarket(ModelForm):
	class Meta:
		model = Market

class FormInvoice(ModelForm):
	class Meta:
		model = Invoice

class FormInvoceGoods(ModelForm):
	class Meta:
		model = InvoiceGoods

class FormProvider(ModelForm):
    class Meta:
        model = Provider

class FormMeasure(ModelForm):
    class Meta:
        model = Measure

class FormGoodsType(ModelForm):
	class Meta:
		model = GoodsType

class FormGoods(ModelForm):
	class Meta:
		model = Goods