# -*- coding: utf-8 -*-
from datetime import datetime, date

from django.db import models
from django.conf import settings

class DepartmentsNames(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.IntegerField(default=1,)
	name = models.CharField(max_length=30, null=True, blank=True)

	def __unicode__(self):
		return unicode(self.name)

	@classmethod
	def list(cls, ):
		res = dict()
		for dep in settings.DEPARTMENTS:
			try:
				name = DepartmentsNames.objects.get(id=int(dep)).name
			except DepartmentsNames.DoesNotExist:
				name = u''
			res[dep] = name
		return res