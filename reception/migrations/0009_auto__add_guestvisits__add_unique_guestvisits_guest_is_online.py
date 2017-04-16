# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GuestVisits'
        db.create_table(u'reception_guestvisits', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('locker', self.gf('django.db.models.fields.IntegerField')()),
            ('guest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reception.Guest'])),
            ('is_online', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal(u'reception', ['GuestVisits'])

        # Adding unique constraint on 'GuestVisits', fields ['guest', 'is_online']
        db.create_unique(u'reception_guestvisits', ['guest_id', 'is_online'])


    def backwards(self, orm):
        # Removing unique constraint on 'GuestVisits', fields ['guest', 'is_online']
        db.delete_unique(u'reception_guestvisits', ['guest_id', 'is_online'])

        # Deleting model 'GuestVisits'
        db.delete_table(u'reception_guestvisits')


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
            'card': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Client']"}),
            'contract_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.ContractType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.Discount']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_current': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'is_open_date': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'pay_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.PayPlan']", 'null': 'True', 'blank': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contract_payer'", 'to': u"orm['person.Client']"}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'contract.contracttype': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'ContractType'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_child': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_visit': ('django.db.models.fields.IntegerField', [], {}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'period_activation': ('django.db.models.fields.IntegerField', [], {}),
            'period_days': ('django.db.models.fields.SmallIntegerField', [], {}),
            'period_freeze': ('django.db.models.fields.IntegerField', [], {}),
            'period_time_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.PeriodTimeType']"}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'contract.discount': {
            'Meta': {'unique_together': "(('value', 'date_start'),)", 'object_name': 'Discount'},
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'contract.payplan': {
            'Meta': {'object_name': 'PayPlan'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'plantype': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'contract.periodtimetype': {
            'Meta': {'object_name': 'PeriodTimeType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'core.user': {
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
        u'person.client': {
            'Meta': {'unique_together': "(('first_name', 'last_name', 'patronymic', 'born_date'),)", 'object_name': 'Client'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'born_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'gender': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'passport': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'patronymic': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        u'reception.guest': {
            'Meta': {'unique_together': "(('firstname', 'lastname', 'patronymic', 'born'),)", 'object_name': 'Guest'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'born': ('django.db.models.fields.DateField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'g_manager'", 'to': u"orm['core.User']"}),
            'patronymic': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.IntegerField', [], {})
        },
        u'reception.guestvisits': {
            'Meta': {'unique_together': "(('guest', 'is_online'),)", 'object_name': 'GuestVisits'},
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {}),
            'guest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reception.Guest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'locker': ('django.db.models.fields.IntegerField', [], {})
        },
        u'reception.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.Contract']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'guest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reception.Guest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_free': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'reception.readby': {
            'Meta': {'object_name': 'ReadBy'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'readtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reminder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reception.Reminder']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'reception.reminder': {
            'Meta': {'object_name': 'Reminder'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_everyday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'wdays': ('django.db.models.fields.CharField', [], {'max_length': '14', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['reception']