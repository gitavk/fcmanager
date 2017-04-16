# -*- coding: utf-8 -*-
from django.db import models

from django.conf import settings
from contract.models import *
from person.models import *
from finance.models import *


class ContractEnd(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(
        max_length=30, blank=False, null=False, unique=True)
    date = models.DateTimeField(default=datetime.now)
    date_joined = models.DateTimeField(default=datetime.now)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_start = models.DateField(default=datetime.now)
    date_end = models.DateField()
    date_finish = models.DateField()
    contract_type = models.ForeignKey(ContractType)
    client = models.ForeignKey(Client)

    class Meta:
        db_table = 'v_contract_end'
        managed = False


class ManagerSells(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=datetime.now)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL)
    contract = models.ForeignKey(Contract)
    client = models.ForeignKey(Client)
    firstptt = models.SmallIntegerField()
    selltype = models.SmallIntegerField()
    goods = models.ForeignKey(Goods)
    amount = models.FloatField()

    class Meta:
        db_table = 'v_manager_sells'
        managed = False
