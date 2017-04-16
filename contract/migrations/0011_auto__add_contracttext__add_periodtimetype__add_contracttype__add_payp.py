# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContractText'
        db.create_table(u'contract_contracttext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('firstpage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('secondpage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'contract', ['ContractText'])

        # Adding model 'PeriodTimeType'
        db.create_table(u'contract_periodtimetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'contract', ['PeriodTimeType'])

        # Adding model 'ContractType'
        db.create_table(u'contract_contracttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('period_days', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('price', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('period_freeze', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('period_activation', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('max_visit', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('period_time_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PeriodTimeType'])),
        ))
        db.send_create_signal(u'contract', ['ContractType'])

        # Adding model 'PayPlanSteps'
        db.create_table(u'contract_payplansteps', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pay_plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PayPlan'])),
            ('number', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'contract', ['PayPlanSteps'])

        # Adding unique constraint on 'PayPlanSteps', fields ['pay_plan', 'number']
        db.create_unique(u'contract_payplansteps', ['pay_plan_id', 'number'])

        # Adding model 'Contract'
        db.create_table(u'contract_contract', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_start', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('contract_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.ContractType'])),
            ('card', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('discount', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('pay_plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PayPlan'], null=True, blank=True)),
            ('payment_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['person.Client'])),
            ('payment_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'contract', ['Contract'])

        # Adding model 'PeriodTime'
        db.create_table(u'contract_periodtime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period_time_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PeriodTimeType'])),
            ('period_visit_start', self.gf('django.db.models.fields.TimeField')()),
            ('period_visit_end', self.gf('django.db.models.fields.TimeField')()),
            ('period_visit_wday', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'contract', ['PeriodTime'])

        # Adding model 'PayPlan'
        db.create_table(u'contract_payplan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('plantype', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'contract', ['PayPlan'])


    def backwards(self, orm):
        # Removing unique constraint on 'PayPlanSteps', fields ['pay_plan', 'number']
        db.delete_unique(u'contract_payplansteps', ['pay_plan_id', 'number'])

        # Deleting model 'ContractText'
        db.delete_table(u'contract_contracttext')

        # Deleting model 'PeriodTimeType'
        db.delete_table(u'contract_periodtimetype')

        # Deleting model 'ContractType'
        db.delete_table(u'contract_contracttype')

        # Deleting model 'PayPlanSteps'
        db.delete_table(u'contract_payplansteps')

        # Deleting model 'Contract'
        db.delete_table(u'contract_contract')

        # Deleting model 'PeriodTime'
        db.delete_table(u'contract_periodtime')

        # Deleting model 'PayPlan'
        db.delete_table(u'contract_payplan')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contract.contract': {
            'Meta': {'object_name': 'Contract'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'card': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Client']"}),
            'contract_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.ContractType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'pay_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.PayPlan']", 'null': 'True', 'blank': 'True'}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'contract.contracttext': {
            'Meta': {'object_name': 'ContractText'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'firstpage': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'secondpage': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'contract.contracttype': {
            'Meta': {'object_name': 'ContractType'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_visit': ('django.db.models.fields.SmallIntegerField', [], {}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'period_activation': ('django.db.models.fields.SmallIntegerField', [], {}),
            'period_days': ('django.db.models.fields.SmallIntegerField', [], {}),
            'period_freeze': ('django.db.models.fields.SmallIntegerField', [], {}),
            'period_time_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.PeriodTimeType']"}),
            'price': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'contract.payplan': {
            'Meta': {'object_name': 'PayPlan'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'plantype': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'contract.payplansteps': {
            'Meta': {'unique_together': "(('pay_plan', 'number'),)", 'object_name': 'PayPlanSteps'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.SmallIntegerField', [], {}),
            'pay_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.PayPlan']"})
        },
        u'contract.periodtime': {
            'Meta': {'object_name': 'PeriodTime'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period_time_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.PeriodTimeType']"}),
            'period_visit_end': ('django.db.models.fields.TimeField', [], {}),
            'period_visit_start': ('django.db.models.fields.TimeField', [], {}),
            'period_visit_wday': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'contract.periodtimetype': {
            'Meta': {'object_name': 'PeriodTimeType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'person.client': {
            'Meta': {'unique_together': "(('first_name', 'last_name', 'patronymic', 'born_date'),)", 'object_name': 'Client'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'born_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'gender': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'passport': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'patronymic': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['contract']