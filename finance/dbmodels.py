from django.db import models

from .models import *

class vIssuanceGoods(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    balance = models.IntegerField()
    expirydate = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'v_issuance_goods'
        managed = False

class vIssuanceGoodsRecovery(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    balance = models.IntegerField()
    count = models.IntegerField()
    expirydate = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'v_issuance_goods_recovery'
        managed = False