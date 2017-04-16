# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'client'
        db.delete_table(u'person_client')


    def backwards(self, orm):
        # Adding model 'client'
        db.create_table(u'person_client', (
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('patronymic', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('gender', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('passport', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('born_date', self.gf('django.db.models.fields.DateField')(blank=True)),
        ))
        db.send_create_signal(u'person', ['client'])


    models = {
        
    }

    complete_apps = ['person']