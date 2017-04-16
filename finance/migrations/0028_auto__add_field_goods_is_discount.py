# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Goods.is_discount'
        db.add_column(u'finance_goods', 'is_discount',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Goods.is_discount'
        db.delete_column(u'finance_goods', 'is_discount')


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
        u'employees.employee': {
            'Meta': {'unique_together': "(('firstname', 'lastname', 'patronymic', 'born'),)", 'object_name': 'Employee'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'born': ('django.db.models.fields.DateField', [], {}),
            'card': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'login': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'patronymic': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'employees.position': {
            'Meta': {'object_name': 'Position'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'finance.barcode': {
            'Meta': {'object_name': 'BarCode'},
            'code': ('django.db.models.fields.DecimalField', [], {'unique': 'True', 'max_digits': '15', 'decimal_places': '0'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'finance.credits': {
            'Meta': {'object_name': 'Credits'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Client']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.Contract']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Employee']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'guest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reception.Guest']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'plan_date': ('django.db.models.fields.DateTimeField', [], {}),
            'ptt_card': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'finance.creditshistory': {
            'Meta': {'object_name': 'CreditsHistory'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Client']", 'null': 'True', 'blank': 'True'}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contract.Contract']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Employee']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'guest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reception.Guest']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'payment_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ch_payment_user'", 'to': u"orm['core.User']"}),
            'plan_date': ('django.db.models.fields.DateTimeField', [], {}),
            'ptt_card': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'finance.goods': {
            'Meta': {'object_name': 'Goods'},
            'department': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'goods_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.GoodsType']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_discount': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Measure']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'mix_measure': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mix_measure'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['finance.Measure']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'finance.goodsprovider': {
            'Meta': {'unique_together': "(('goods', 'provider'),)", 'object_name': 'GoodsProvider'},
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Provider']"})
        },
        u'finance.goodstype': {
            'Meta': {'object_name': 'GoodsType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'finance.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'on_delete': 'models.PROTECT'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Provider']", 'on_delete': 'models.PROTECT'})
        },
        u'finance.invoicegoods': {
            'Meta': {'object_name': 'InvoiceGoods'},
            'balance': ('django.db.models.fields.IntegerField', [], {}),
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'expirydate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Invoice']", 'on_delete': 'models.PROTECT'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'finance.issuance': {
            'Meta': {'object_name': 'Issuance'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'on_delete': 'models.PROTECT'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Market']", 'on_delete': 'models.PROTECT'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'finance.issuancegoods': {
            'Meta': {'object_name': 'IssuanceGoods'},
            'balance': ('django.db.models.fields.IntegerField', [], {}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.InvoiceGoods']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Issuance']", 'on_delete': 'models.PROTECT'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'finance.market': {
            'Meta': {'object_name': 'Market'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'finance.measure': {
            'Meta': {'object_name': 'Measure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'finance.positionptt': {
            'Meta': {'object_name': 'PositionPTT'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Position']", 'on_delete': 'models.PROTECT'})
        },
        u'finance.price': {
            'Meta': {'unique_together': "(('goods', 'is_active'),)", 'object_name': 'Price'},
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['finance.Goods']", 'on_delete': 'models.PROTECT'}),
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['finance']