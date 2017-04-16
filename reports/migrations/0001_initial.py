# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DepartmentsNames'
        db.create_table(u'reports_departmentsnames', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('department', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'reports', ['DepartmentsNames'])


    def backwards(self, orm):
        # Deleting model 'DepartmentsNames'
        db.delete_table(u'reports_departmentsnames')


    models = {
        u'reports.departmentsnames': {
            'Meta': {'object_name': 'DepartmentsNames'},
            'department': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['reports']