# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg, Max, Min

from person.models import Client


class Discount(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    date_start = models.DateField(default=date.today)
    date_end = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("value", "date_start")


class PeriodTimeType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False, null=False)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)


class PeriodTime(models.Model):
    period_time_type = models.ForeignKey(PeriodTimeType)
    period_visit_start = models.TimeField()
    period_visit_end = models.TimeField()
    period_visit_wday = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(6)])


class ContractText(models.Model):

    """docstring for ContractText"""
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now=True)
    person = models.ForeignKey(settings.AUTH_USER_MODEL)
    firstpage = models.ImageField(upload_to="contracttext/", blank=True)
    secondpage = models.ImageField(upload_to="contracttext/", blank=True)

    class Meta:
        get_latest_by = "id"


class ContractType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    period_days = models.SmallIntegerField()
    price = models.IntegerField()
    period_freeze = models.IntegerField()
    period_activation = models.IntegerField()
    max_visit = models.IntegerField()
    period_time_type = models.ForeignKey(PeriodTimeType)
    is_active = models.BooleanField(default=True)
    date_start = models.DateTimeField()
    version = models.IntegerField(default=0)
    is_child = models.BooleanField(default=False)
    # text = models.ForeignKey(ContractText)

    class Meta:
        unique_together = ("name", "version")


class PayPlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=30, blank=False, null=False, unique=True)
    plantype = models.SmallIntegerField(default=0)
    """ pay plan type:
		0 == by value
		1 == by percentage
		2 == custom
	"""
    is_active = models.BooleanField(default=True)
    amount = models.FloatField(default=0.0)

    def __unicode__(self):
        return unicode(self.name)


class PayPlanSteps(models.Model):
    pay_plan = models.ForeignKey(PayPlan)
    number = models.SmallIntegerField()
    amount = models.FloatField()

    class Meta:
        unique_together = ("pay_plan", "number")


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(
        max_length=30, blank=False, null=False, unique=True)
    date = models.DateTimeField(default=datetime.now)
    date_joined = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    """
	UPDATE contract_contract SET date_joined = date;
	"""
    manager = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_start = models.DateField(default=datetime.now)
    date_end = models.DateField()
    contract_type = models.ForeignKey(ContractType)
    card = models.BigIntegerField(blank=True, null=True)
    amount = models.FloatField()
    pay_plan = models.ForeignKey(PayPlan, blank=True, null=True, )
    payment_date = models.DateTimeField()
    client = models.ForeignKey(Client)
    payer = models.ForeignKey(Client, related_name='contract_payer')
    discount = models.ForeignKey(Discount, blank=True, null=True)
    is_open_date = models.BooleanField(default=False)
    bonus_visit = models.IntegerField(default=0, blank=True, null=True)

    is_current = models.SmallIntegerField(default=2)
    """ is_current : 
		0 == old
		1 == current
		2 == prospect
		3 == ban
	"""

    payment_type = models.SmallIntegerField(default=0)
    """ payment_type : 
		0 == cash
		1 == cashless
		2 == other way
	"""
    class Meta:
        get_latest_by = "id"

    def activate(self):
        time_delta = self.date_end - self.date_start
        self.date_start = date.today()
        self.date_end = self.date_start + time_delta
        self.is_current = 1
        self.save()
        return 1

    def close(self):
        self.date_end = date.today()
        self.is_current = 0
        self.save()
        # change date of activation countdown
        for p in Contract.objects.filter(is_current=2, client=self.client
                                         ).order_by('date_joined'):
            p.date = self.date_end + timedelta(days=1)
            p.save()
        return 1

    def days_period(self):
        return (self.date_end - self.date_start).days

    def days_left(self):
        return (self.date_end - date.today()).days

    def date_finish(self):
        return self.date_end - timedelta(days=1)

    def first_visit(self):
        v = Visits.objects.filter(contract=self).order_by('date_start')
        if v.count() > 0:
            return v[0].date_start.date()
        else:
            return None

    def visits_left(self):
        if self.bonus_visit:
            max_visit = self.contract_type.max_visit + self.bonus_visit
        else:
            max_visit = self.contract_type.max_visit

        return max_visit - Visits.objects.filter(contract=self).count()

    def visits_use(self):
        return Visits.objects.filter(contract=self).count()

    def freeze_left(self):
        freeze_sum = 0
        for f in Freeze.objects.filter(contract=self):
            freeze_sum += f.days()
        period_freeze = self.contract_type.period_freeze
        # find payment freeze
        chs = self.creditshistory_set.exclude(goods__isnull=True)
        for ch in chs:
            if ch.goods.is_pay_freeze:
                period_freeze += ch.goods.pay_days
        return period_freeze - freeze_sum

    def is_freeze(self):
        if Freeze.objects.filter(contract=self,
                                 is_closed=False,
                                 date_end__gte=date.today(),
                                 date_start__lte=date.today(),
                                 ).count():
            stdate = Freeze.objects.filter(
                contract=self, is_closed=False).aggregate(Min('date_start'))
            if stdate['date_start__min'] > date.today():
                return 0
            else:
                endate = Freeze.objects.filter(
                    contract=self, is_closed=False).aggregate(Min('date_end'))
                return endate['date_end__min']
        else:
            return 0

    def freeze_end(self):
        if self.is_freeze():
            endate = Freeze.objects.filter(
                contract=self,
                date_end__gte=date.today(),
                date_start__lte=date.today(),
                is_closed=False).aggregate(Max('date_end'))
            if endate['date_end__max']:
                if endate['date_end__max'] >= date.today():
                    return endate['date_end__max']

        return date.today() - timedelta(days=1000)

    def freeze(self, date_start, days):
        days = int(days)
        if days > self.freeze_left():
            return 0
        else:
            if date_start <= self.freeze_end():
                return 0
            freeze = Freeze(
                contract=self, date_start=date_start,
                date_end=date_start + timedelta(days=days))
            freeze.save()
            self.date_end = self.date_end + timedelta(days=days)
            self.save()
            return 1

    def ban(self, date_end, note, manager):
        ban = Ban(contract=self, manager=manager,
                  date_end=date_end, note=note,)
        ban.save()
        self.date_end = date_end
        self.is_current = 3
        self.save()

    def ban_info(self):
        if self.is_current == 3:
            try:
                res = Ban.objects.get(contract=self)
            except Ban.DoesNotExist:
                return 0
            d_end = res.date_end.strftime("%d.%m.%Y")
            note = unicode(res.note)
            return '%s :: %s' % (d_end, note)
        else:
            return 0

    def bonus(self, date_start, days, visits, note, manager):
        days = int(days)
        if days < 0:
            days = 0
        visits = int(visits)
        if self.contract_type.max_visit == 99999:
            visits = 0

        bonus = Bonus(contract=self, manager=manager,
                      date_start=date_start,
                      date_end=date_start + timedelta(days=days),
                      visits=visits, note=note,)
        bonus.save()
        self.date_end = self.date_end + timedelta(days=days)
        if self.bonus_visit:
            self.bonus_visit = self.bonus_visit + visits
        else:
            self.bonus_visit = visits
        self.save()
        return 1

    def is_first(self):
        first = Contract.objects.filter(
            client=self.client).aggregate(Min('pk'))
        if first['pk__min'] == self.pk:
            return 1
        else:
            return 0

    def save(self, *args, **kwargs):
        is_ban = Ban.objects.filter(contract=self).count()
        if is_ban > 0:
            self.is_current = 3
        else:
            cnt_current = Contract.objects.filter(
                client=self.client, is_current=1).exclude(pk=self.pk).count()
            if cnt_current > 0:
                self.is_current = 2
            if self.is_current == 2 and cnt_current > 0:
                dstart = Contract.objects.filter(client=self.client, ).exclude(
                    pk=self.pk).aggregate(Max('date_end'))
                if dstart['date_end__max']:
                    self.date_start = dstart[
                        'date_end__max'] + timedelta(days=1)
                    days = self.contract_type.period_days
                    self.date_end = self.date_start + timedelta(days=days)
        super(Contract, self).save(*args, **kwargs)


class Ban(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(
        Contract, on_delete=models.PROTECT, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_end = models.DateField(blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)


class Bonus(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    visits = models.IntegerField(blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)


class Freeze(models.Model):
    id = models.AutoField(primary_key=True)
    date_start = models.DateField(default=date.today())
    date_end = models.DateField()
    contract = models.ForeignKey(Contract)
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("date_start", "contract")

    def close(self):
        if self.date_end > date.today():
            deltadays = (self.date_end - date.today()).days
            self.contract.date_end = self.contract.date_end - \
                timedelta(days=deltadays)
            self.contract.save()
            self.date_end = date.today()

        self.is_closed = True
        self.save()

    def days(self):
        return (self.date_end - self.date_start).days


class Visits(models.Model):
    id = models.AutoField(primary_key=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    locker = models.IntegerField()
    gender = models.SmallIntegerField()
    contract = models.ForeignKey(Contract)
    is_online = models.IntegerField(default=-1)

    def out(self):
        self.date_end = datetime.now()
        self.is_online = self.id

    class Meta:
        unique_together = ("contract", "is_online")
