# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.conf import settings

class Guest(models.Model):
	id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=30, blank=True, null=True)
	last_name = models.CharField(max_length=30, blank=True, null=True)
	patronymic = models.CharField(max_length=30, blank=True, null=True)
	phone = models.BigIntegerField(unique=True)
	manager = models.ForeignKey(settings.AUTH_USER_MODEL)
	note = models.CharField(max_length=100, blank=True, null=True)
	date = models.DateTimeField(default=datetime.now)
	is_client = models.SmallIntegerField(default=0)
	gtype = models.SmallIntegerField(default=0)
	"""
	0 == guest
	1 == incoming call
	2 == out call
	"""
	def is_client_str(self):
		return u'Да' if self.is_client else u'Нет'

	def gtype_str(self):
		if self.gtype == 0:
			return 'гость'
		elif self.gtype == 1:
			return 'входящий звонок'
		else:
			return 'исходящий звонок'

	def get_full_name(self):
		full_name = '%s %s' % (self.last_name , self.first_name)
		return full_name.strip()

	def fullname(self):
		fname = '%s %s %s' % (
			self.last_name , self.first_name, self.patronymic)
		return fname

class Note(models.Model):
	id = models.AutoField(primary_key=True)
	text = models.CharField(max_length=500)
	date = models.DateTimeField(default=datetime.now)
	author = models.ForeignKey(settings.AUTH_USER_MODEL)
	datetodo = models.DateField(default=datetime.today)
	note_type = models.SmallIntegerField(default=0)
	"""
	note_type == 0 simple Note
	note_type == 1 notification

	"""

class NoteUsers(models.Model):
	note = models.ForeignKey(Note)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	is_read = models.SmallIntegerField(default=0)

	class Meta:
		unique_together = ("note", "user")