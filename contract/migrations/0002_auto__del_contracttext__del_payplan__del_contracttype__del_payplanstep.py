# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'PayPlanSteps', fields ['pay_plan', 'number']
        db.delete_unique(u'contract_payplansteps', ['pay_plan_id', 'number'])

        # Deleting model 'ContractText'
        db.delete_table(u'contract_contracttext')

        # Deleting model 'PayPlan'
        db.delete_table(u'contract_payplan')

        # Deleting model 'ContractType'
        db.delete_table(u'contract_contracttype')

        # Deleting model 'PayPlanSteps'
        db.delete_table(u'contract_payplansteps')

        # Deleting model 'Contract'
        db.delete_table(u'contract_contract')

        # Deleting model 'PeriodTime'
        db.delete_table(u'contract_periodtime')

        # Deleting model 'PeriodTimeType'
        db.delete_table(u'contract_periodtimetype')


    def backwards(self, orm):
        # Adding model 'ContractText'
        db.create_table(u'contract_contracttext', (
            ('firstpage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('secondpage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'contract', ['ContractText'])

        # Adding model 'PayPlan'
        db.create_table(u'contract_payplan', (
            ('plantype', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True)),
        ))
        db.send_create_signal(u'contract', ['PayPlan'])

        # Adding model 'ContractType'
        db.create_table(u'contract_contracttype', (
            ('price', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('max_visit', self.gf('django.db.models.fields.SmallIntegerField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period_activation', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('period_days', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True)),
            ('period_freeze', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('period_time_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PeriodTimeType'])),
        ))
        db.send_create_signal(u'contract', ['ContractType'])

        # Adding model 'PayPlanSteps'
        db.create_table(u'contract_payplansteps', (
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('pay_plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PayPlan'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'contract', ['PayPlanSteps'])

        # Adding unique constraint on 'PayPlanSteps', fields ['pay_plan', 'number']
        db.create_unique(u'contract_payplansteps', ['pay_plan_id', 'number'])

        # Adding model 'Contract'
        db.create_table(u'contract_contract', (
            ('date_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True)),
            ('contract_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.ContractType'])),
            ('discount', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('card', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('payment_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_start', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('payment_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('pay_plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PayPlan'])),
        ))
        db.send_create_signal(u'contract', ['Contract'])

        # Adding model 'PeriodTime'
        db.create_table(u'contract_periodtime', (
            ('period_visit_start', self.gf('django.db.models.fields.TimeField')()),
            ('period_visit_end', self.gf('django.db.models.fields.TimeField')()),
            ('period_visit_wday', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('period_time_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.PeriodTimeType'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'contract', ['PeriodTime'])

        # Adding model 'PeriodTimeType'
        db.create_table(u'contract_periodtimetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'contract', ['PeriodTimeType'])


    models = {
        
    }

    complete_apps = ['contract']