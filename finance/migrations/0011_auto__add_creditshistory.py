# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CreditsHistory'
        db.create_table(u'finance_creditshistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'])),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('plan_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('contract', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contract.Contract'], null=True, blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['person.Client'], null=True, blank=True)),
            ('payment_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('payment_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('payment_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ch_payment_user', to=orm['core.User'])),
        ))
        db.send_create_signal(u'finance', ['CreditsHistory'])


    def backwards(self, orm):
        # Deleting model 'CreditsHistory'
        db.delete_table(u'finance_creditshistory')


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
            'card': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
        u'finance.barcode': {
            'Meta': {'object_name': 'BarCode'},
            'code': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '0'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'finance.credits': {
            'Meta': {'object_name': 'Credits'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Client']", 'null': 'True', 'blank': 'True'}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.Contract']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'plan_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'finance.creditshistory': {
            'Meta': {'object_name': 'CreditsHistory'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Client']", 'null': 'True', 'blank': 'True'}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.Contract']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'payment_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ch_payment_user'", 'to': u"orm['core.User']"}),
            'plan_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'finance.goods': {
            'Meta': {'object_name': 'Goods'},
            'goods_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.GoodsType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Measure']", 'null': 'True', 'blank': 'True'}),
            'mix_measure': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mix_measure'", 'null': 'True', 'to': u"orm['finance.Measure']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'register_units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.RegisterUnits']", 'null': 'True', 'blank': 'True'})
        },
        u'finance.goodsprovider': {
            'Meta': {'unique_together': "(('goods', 'provider'),)", 'object_name': 'GoodsProvider'},
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Provider']"})
        },
        u'finance.goodstype': {
            'Meta': {'object_name': 'GoodsType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'finance.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Provider']"})
        },
        u'finance.invoicegoods': {
            'Meta': {'object_name': 'InvoiceGoods'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'expirydate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Invoice']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'finance.measure': {
            'Meta': {'object_name': 'Measure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'finance.price': {
            'Meta': {'unique_together': "(('goods', 'is_active'),)", 'object_name': 'Price'},
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'})
        },
        u'finance.provider': {
            'Meta': {'object_name': 'Provider'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inn': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '0', 'blank': 'True'}),
            'kpp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'finance.registerunits': {
            'Meta': {'object_name': 'RegisterUnits'},
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
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'passport': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'patronymic': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        }
    }

    complete_apps = ['finance']