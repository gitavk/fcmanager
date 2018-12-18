# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db import models
from django.db.models import Max, Min, Sum, Q
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

from person.models import Client
from contract.models import Contract
from reception.models import Guest
from employees.models import Employee, Position


SYS_GOODS = ['SERVICE', 'PTT', '1PTT']


class GoodsType(models.Model):

    """
     need add name = SERVICE
     for system type not delete, not edit
     need add name = PTT, 1PTT
     (personal trainer)
     for system type not delete, not edit
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    note = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(GoodsType, self).save(*args, **kwargs)


class Measure(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    note = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Measure, self).save(*args, **kwargs)


class Provider(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    inn = models.DecimalField(
        max_digits=15, decimal_places=0, blank=True, null=True)
    kpp = models.DecimalField(
        max_digits=15, decimal_places=0, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    activity = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Provider, self).save(*args, **kwargs)


class Goods(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    goods_type = models.ForeignKey(
        GoodsType, blank=True, null=True, on_delete=models.PROTECT)
    measure = models.ForeignKey(
        Measure, blank=True, null=True, on_delete=models.PROTECT)
    mix_measure = models.ForeignKey(
        Measure, blank=True, null=True, on_delete=models.PROTECT,
        related_name='mix_measure')
    # department validators by cash driver for shtrih-m
    department = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(16)])
    # need for personal training number (add letter A)
    is_discount = models.SmallIntegerField(default=0)
    # this goods only for active contract
    client_only = models.SmallIntegerField(default=0)
    # nedd for add invite for client without contract
    single_visit = models.SmallIntegerField(default=0)
    # for pay freeze
    is_pay_freeze = models.BooleanField(default=False, blank=True)
    pay_days = models.SmallIntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def cash_name(self):
        return unicode(self.name.replace('"', ''))

    def in_stock(self):
        b = InvoiceGoods.objects.filter(
            goods=self, balance__gt=0).aggregate(Sum('balance'))
        if b['balance__sum']:
            return b['balance__sum']
        else:
            return 0

    def on_market(self):
        if self.goods_type.name in ['SERVICE', '1PTT']:
            return 1
        else:
            i = InvoiceGoods.objects.filter(goods=self)
            b = IssuanceGoods.objects.filter(
                goods__in=i).exclude(balance=0).aggregate(Sum('balance'))
            if b['balance__sum']:
                return b['balance__sum']
            else:
                return 0

    def new_price(self, value, date_start):
        new_is_active = -1  # default new price is active
        try:
            old_price = Price.objects.get(goods=self, is_active=-1)
            old_price.date_end = date_start
            if date_start <= datetime.today().date():
                old_price.is_active = old_price.id
            else:
                new_is_active = 0
            old_price.save()
        except Price.DoesNotExist:
            pass  # don't need update old price

        Price(
            goods=self, value=value, date_start=date_start,
            is_active=new_is_active).save()
        return 1

    def priceondate(self, date):
        prices = Price.objects.filter(
            Q(date_start__lte=date), Q(goods=self),
            (Q(date_end__isnull=True) | Q(date_end__gt=date)),
        )
        return prices[0].value if prices else 0

    def price(self):
        try:
            return Price.objects.get(goods=self, is_active=-1).value
        except Price.DoesNotExist:
            return -1

    def price_date(self):
        try:
            return Price.objects.get(goods=self, is_active=-1).date_start
        except Price.DoesNotExist:
            return datetime.now

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Goods, self).save(*args, **kwargs)


class PositionPTT(models.Model):

    """list  the positions of employees  for goods type PTT"""
    id = models.AutoField(primary_key=True)
    position = models.ForeignKey(Position, on_delete=models.PROTECT)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)


class GoodsProvider(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    provider = models.ForeignKey(Provider)

    class Meta:
        unique_together = ("goods", "provider")


class BarCode(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    code = models.DecimalField(max_digits=15, decimal_places=0, unique=True)


class Price(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    date_start = models.DateField(default=datetime.now)
    date_end = models.DateField(blank=True, null=True)
    is_active = models.IntegerField(default=-1)
    value = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ("goods", "is_active")


class Invitation(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, blank=True, null=True)
    client = models.ForeignKey(Client, blank=True, null=True)
    contract = models.ForeignKey(Contract, blank=True, null=True)
    date = models.DateTimeField()
    is_free = models.BooleanField(default=True)

    def used(self):
        return Invitation.objects.filter(contract=self.contract).count()


class Credits(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    plan_date = models.DateTimeField()
    goods = models.ForeignKey(
        Goods, blank=True, null=True, on_delete=models.PROTECT)
    count = models.IntegerField(
        default=1, validators=[MinValueValidator(0)])
    contract = models.ForeignKey(
        Contract, blank=True, null=True, on_delete=models.PROTECT)
    client = models.ForeignKey(
        Client, blank=True, null=True, on_delete=models.PROTECT)
    guest = models.ForeignKey(
        Guest, blank=True, null=True, on_delete=models.PROTECT)
    # employee ==> trainer for personal training
    employee = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.PROTECT)
    ptt_card = models.BigIntegerField(blank=True, null=True, unique=True)
    department = models.IntegerField(default=1)

    payment_type = models.SmallIntegerField(default=0)
    """ payment_type:
        0 == cash
        1 == cashless
        2 == other way
    """

    def g_amount(self):
        return round(self.amount / self.count, 2)

    def escape(self):
        if self.goods:
            is_not_sys = self.goods.goods_type.name not in SYS_GOODS
            if is_not_sys and not self.goods.is_pay_freeze:
                cnt = self.count
                invoice = InvoiceGoods.objects.filter(goods=self.goods)
                for ig in IssuanceGoods.objects.filter(
                        goods__in=invoice).order_by('-id'):
                    if ig.count > ig.balance:
                        delta = ig.count - ig.balance
                        if cnt > delta:
                            ig.balance = ig.count
                            cnt -= delta
                            ig.save()
                        elif cnt <= delta:
                            ig.balance += cnt
                            ig.save()
                            break
        self.delete()

    def save(self, *args, **kwargs):
        if self.goods:
            is_not_sys = self.goods.goods_type.name not in SYS_GOODS
            enough = self.goods.on_market() > self.count
            if is_not_sys and not self.goods.is_pay_freeze and not enough:
                msg = u'%s is too big max: %s' % (
                    self.count, self.goods.on_market())
                raise ValidationError(msg)
            elif is_not_sys and not self.goods.is_pay_freeze:
                cnt = self.count
                invoice = InvoiceGoods.objects.filter(goods=self.goods)
                for ig in IssuanceGoods.objects.filter(
                        goods__in=invoice, balance__gt=0).order_by('id'):
                    if cnt > ig.balance:
                        cnt -= ig.balance
                        ig.balance = 0
                        ig.save()
                    else:
                        ig.balance -= cnt
                        ig.save()
                        break
            if self.goods.goods_type.name == 'PTT' and self.amount > 0:
                pass
            else:
                self.amount = self.count * self.goods.price()
        super(Credits, self).save(*args, **kwargs)

    def close(self, user, payment_type, cc=None):
        if self.goods:
            if self.goods.single_visit:
                i = Invitation(
                    guest=self.guest, client=self.client,
                    contract=self.contract, date=datetime.now(),
                    is_free=True)
                i.save()

        ch = CreditsHistory(
            user=self.user, amount=self.amount, plan_date=self.plan_date,
            goods=self.goods, count=self.count, contract=self.contract,
            client=self.client, guest=self.guest, employee=self.employee,
            ptt_card=self.ptt_card, payment_user=user,
            payment_type=payment_type, department=self.department, check=cc)
        ch.save()
        self.delete()


class CashCheck(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)

    def credits_list(self):
        return CreditsHistory.objects.filter(check=self).order_by('date')

    def credits_list_str(self):
        res = ''
        for ch in CreditsHistory.objects.filter(check=self).order_by('date'):
            res += 'cr' + str(ch.pk) + '|' + \
                ch.cash_name() + '|' + \
                str(ch.count) + '|' + \
                str(ch.amount) + '|' + \
                str(ch.cash_department()) + '|'
        return res

    def username(self):
        return CreditsHistory.objects.filter(check=self)[0].username()

    def payment_type(self):
        return CreditsHistory.objects.filter(check=self)[0].payment_type

    def cash_payment_type(self):
        if self.payment_type() == 0:
            return 1
        elif self.payment_type() == 1:
            return 2
        else:
            return None

    def count(self):
        return CreditsHistory.objects.filter(check=self).count()

    def amount(self):
        s = CreditsHistory.objects.filter(check=self).aggregate(Sum('amount'))
        return s['amount__sum']

    def number(self):
        previous_d = self.date.date() - timedelta(days=1)
        last = CashCheck.objects.filter(
            date__year=previous_d.year,
            date__month=previous_d.month,
            date__day=previous_d.day).aggregate(Max('pk'))
        if not last['pk__max']:
            last = CashCheck.objects.filter(
                date__lt=previous_d).aggregate(Max('pk'))
        if not last['pk__max']:
            previous_max = 0
        else:
            previous_max = last['pk__max']
        return self.id - previous_max

    def cash_rollback(self):
        """
        return three status:
        0 - can't
        1 - can
        2 - already done
        """
        cnt_return = CreditsHistory.objects.filter(
            check=self, is_return=1).count()
        if cnt_return == self.count():
            return 2
        elif cnt_return > 0:
            # because one or more payment already returned
            return 0
        else:
            if self.date.date() == datetime.now().date()\
                    and self.payment_type() != 2:
                return 1
            else:
                return 0

    def rollback(self):
        for ch in CreditsHistory.objects.filter(check=self).order_by('date'):
            ch.rollback()
        return 1


class CreditsHistory(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    check = models.ForeignKey(
        CashCheck, blank=True, null=True, on_delete=models.PROTECT)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    goods = models.ForeignKey(
        Goods, blank=True, null=True, on_delete=models.PROTECT)
    count = models.IntegerField(
        default=1, validators=[MinValueValidator(0)])
    plan_date = models.DateTimeField()
    contract = models.ForeignKey(Contract, blank=True, null=True)
    client = models.ForeignKey(Client, blank=True, null=True)
    guest = models.ForeignKey(Guest, blank=True, null=True)
    employee = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.PROTECT)
    ptt_card = models.BigIntegerField(blank=True, null=True, unique=True)
    payment_type = models.SmallIntegerField(default=0)
    """ payment_type:
        0 == cash
        1 == cashless
        2 == other way
    """
    department = models.IntegerField(default=1)
    # for rollbak credits
    is_return = models.SmallIntegerField(default=0)
    date_return = models.DateTimeField(blank=True, null=True)
    user_return = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='ch_user_return',
        on_delete=models.PROTECT, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='ch_payment_user')

    def username(self):
        if self.client:
            return self.client.initials()
        elif self.guest:
            return self.guest.initials()
        elif self.contract:
            return self.contract.client.initials()
        else:
            return u''

    def goodsprice(self):
        if self.goods:
            return self.goods.priceondate(self.date)
        else:
            return self.contract.amount

    def cash_name(self):
        if self.goods:
            return self.goods.name
        else:
            return u'Абонемент'

    def cash_department(self):
        if self.goods:
            return self.department
        else:
            return 1

    def cash_payment_type(self):
        if self.payment_type == 0:
            return 1
        elif self.payment_type == 1:
            return 2
        else:
            return None

    def goodsname(self):
        if self.goods:
            return self.goods.name
        else:
            return u'Договор #%s' % self.contract.number

    def cash_rollback(self):
        """
        return three status:
        0 - can't
        1 - can
        2 - already done
        """
        if self.is_return == 1:
            return 2
        else:
            if self.payment_date.date() == datetime.now().date()\
                    and self.payment_type != 2:
                return 1
            else:
                return 0

    def rollback(self):
        if self.goods:
            if self.goods.goods_type.name not in SYS_GOODS:
                cnt = self.count
                invoice = InvoiceGoods.objects.filter(goods=self.goods)
                for ig in IssuanceGoods.objects.filter(
                        goods__in=invoice).order_by('-id'):
                    if ig.count > ig.balance:
                        delta = ig.count - ig.balance
                        if cnt > delta:
                            ig.balance = ig.count
                            cnt -= delta
                            ig.save()
                        elif cnt <= delta:
                            ig.balance += cnt
                            ig.save()
                            break
        elif self.contract:
            if self.goods and self.goods.is_pay_freeze:
                pass
            else:
                cr = Credits(
                    user=self.user, amount=self.amount, plan_date=self.plan_date,
                    goods=self.goods, count=self.count, contract=self.contract,
                    client=self.client, guest=self.guest, employee=self.employee,
                    ptt_card=self.ptt_card, payment_type=self.payment_type,
                    department=self.department)
                cr.save()
        self.is_return = 1
        self.amount = 0
        self.save()

    def __unicode__(self):
        return '%s %s %s' % (self.date, self.goodsname(), self.amount)


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=150)
    date = models.DateField()
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.CharField(max_length=150, blank=True, null=True)

    def summ(self):
        result = 0
        for s in InvoiceGoods.objects.filter(invoice=self):
            result += s.count * s.cost
        return result

    def __unicode__(self):
        return unicode(self.number)


class InvoiceGoods(models.Model):
    id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    count = models.IntegerField(validators=[MinValueValidator(0)])
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    expirydate = models.DateField(blank=True, null=True)
    note = models.CharField(max_length=150, blank=True, null=True)
    balance = models.IntegerField(validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        if self.balance > self.count:
            msg = u'%s is too big max: %s' % (self.balance, self.count)
            raise ValidationError(msg)
        else:
            super(InvoiceGoods, self).save(*args, **kwargs)


class Market(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return unicode(self.name)


class Issuance(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.CharField(max_length=150, blank=True, null=True)

    def has_sell(self):
        cnt_sells = 0
        for ig in IssuanceGoods.objects.filter(issuance=self):
            if ig.count > ig.balance:
                cnt_sells += 1
        return cnt_sells

    def number(self):
        previous_y = self.date.year - 1
        last = Issuance.objects.filter(
            date__year=previous_y).aggregate(Max('pk'))
        if last['pk__max']:
            previous_max = last['pk__max']
        else:
            previous_max = 0

        return self.id - previous_max

    def summ(self):
        result = 0
        for s in IssuanceGoods.objects.filter(issuance=self):
            g = InvoiceGoods.objects.get(pk=s.goods)
            result += s.count * g.cost
        return result

    def __unicode__(self):
        return unicode(self.number())


class IssuanceGoods(models.Model):
    id = models.AutoField(primary_key=True)
    issuance = models.ForeignKey(Issuance, on_delete=models.PROTECT)
    goods = models.ForeignKey(InvoiceGoods, on_delete=models.PROTECT)
    count = models.IntegerField(validators=[MinValueValidator(0)])
    note = models.CharField(max_length=150, blank=True, null=True)
    balance = models.IntegerField(validators=[MinValueValidator(0)])

    def to_market(self, *args, **kwargs):
        total_cnt = IssuanceGoods.objects.filter(
            goods=self.goods).exclude(id=self.id).aggregate(Sum('count'))
        if not total_cnt['count__sum']:
            total_cnt['count__sum'] = 0
        total_cnt['count__sum'] += self.count
        self.goods.balance = self.goods.count - total_cnt['count__sum']
        self.goods.save()
        super(IssuanceGoods, self).save(*args, **kwargs)


class Client_PTT(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    is_card = models.SmallIntegerField(default=0)
    payment_type = models.SmallIntegerField(default=0)
    """ payment_type:
        0 == cash
        1 == cashless
        2 == other way
    """

    class Meta:
        get_latest_by = "id"

    def number(self):
        num = self.id + settings.PTT_START
        if self.goods.is_discount:
            return str(num) + u'A'
        else:
            return num

    def is_first(self):
        first = Client_PTT.objects.filter(
            client=self.client).aggregate(Min('pk'))
        if first['pk__min'] == self.pk:
            return 1
        else:
            return 0


class Trash(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.CharField(max_length=150, blank=True, null=True)

    def number(self):
        previous_y = datetime.now().year - 1
        last = Trash.objects.filter(
            date__year=previous_y).aggregate(Max('pk'))
        if last['pk__max']:
            previous_max = last['pk__max']
        else:
            previous_max = 0

        return self.id - previous_max

    def goods_lst(self):
        return TrashGoods.objects.filter(trash=self)


class TrashGoods(models.Model):
    id = models.AutoField(primary_key=True)
    trash = models.ForeignKey(Trash, on_delete=models.PROTECT)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    count = models.IntegerField(validators=[MinValueValidator(0)])
    note = models.CharField(max_length=150, blank=True, null=True)
