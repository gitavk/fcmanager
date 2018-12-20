# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.conf import settings


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    born = models.DateField()
    phone = models.CharField(max_length=32, blank=True, null=True,)
    address = models.CharField(max_length=255, blank=True, null=True,)
    # 9223372036854775807
    card = models.BigIntegerField(blank=True, null=True, unique=True)
    login = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    note = models.CharField(max_length=200, blank=True, null=True)

    def is_online(self):
        if Visits.objects.filter(employee=self, date_end__isnull=True):
            return True
        else:
            return False

    def comein(self):
        if self.is_online():
            for v in Visits.objects.filter(employee=self, date_end__isnull=True):
                v.date_end = datetime.now()
                v.save()
        else:
            Visits(date_start=datetime.now(), employee=self).save()

    class Meta:
        unique_together = ('firstname', 'lastname', 'patronymic', 'born')

    def save(self, *args, **kwargs):
        self.firstname = self.firstname.upper()
        self.lastname = self.lastname.upper()
        self.patronymic = self.patronymic.upper()
        super(Employee, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        return unicode('%s %s' % (self.firstname, self.lastname))

    def initials(self):
        return unicode(
            '%s%s %s. %s.' %
            (
                self.lastname[0],
                self.lastname[1:].lower(),
                self.firstname[0],
                self.patronymic[0]
            )
        )

    def whistory(self):
        return WorkRecord.objects.filter(employee=self).order_by('date_start')

    def currwork(self):
        try:
            return WorkRecord.objects.get(employee=self, date_end__isnull=True)
        except WorkRecord.DoesNotExist:
            return 0


class Visits(models.Model):
    id = models.AutoField(primary_key=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True,)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Department, self).save(*args, **kwargs)


class Position(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True,)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Position, self).save(*args, **kwargs)


class DepartmentPosition(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.ForeignKey(Position, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('position', 'department')


class WorkRecord(models.Model):
    id = models.AutoField(primary_key=True)
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    wposition = models.ForeignKey(DepartmentPosition, on_delete=models.PROTECT)


class Shift(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.SmallIntegerField()
    date = models.DateTimeField()
    time_start = models.TimeField()
    time_end = models.TimeField()

    class Meta:
        unique_together = ('number', 'date')


class Timetable(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('shift', 'date')
