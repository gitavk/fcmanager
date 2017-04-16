# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'DepartmentsNames.name'
        db.alter_column(u'reports_departmentsnames', 'name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True))

    def backwards(self, orm):

        # Changing field 'DepartmentsNames.name'
        db.alter_column(u'reports_departmentsnames', 'name', self.gf('django.db.models.fields.CharField')(default=1, max_length=30))

    models = {
        u'reports.departmentsnames': {
            'Meta': {'object_name': 'DepartmentsNames'},
            'department': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['reports']