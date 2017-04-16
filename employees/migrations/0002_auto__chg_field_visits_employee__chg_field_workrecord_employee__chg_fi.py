# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Visits.employee'
        db.alter_column(u'employees_visits', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Employee'], on_delete=models.PROTECT))

        # Changing field 'WorkRecord.employee'
        db.alter_column(u'employees_workrecord', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Employee'], on_delete=models.PROTECT))

        # Changing field 'WorkRecord.department'
        db.alter_column(u'employees_workrecord', 'department_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Department'], on_delete=models.PROTECT))

        # Changing field 'WorkRecord.position'
        db.alter_column(u'employees_workrecord', 'position_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Position'], on_delete=models.PROTECT))

        # Changing field 'Employee.login'
        db.alter_column(u'employees_employee', 'login_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'], on_delete=models.PROTECT))

    def backwards(self, orm):

        # Changing field 'Visits.employee'
        db.alter_column(u'employees_visits', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Employee']))

        # Changing field 'WorkRecord.employee'
        db.alter_column(u'employees_workrecord', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Employee']))

        # Changing field 'WorkRecord.department'
        db.alter_column(u'employees_workrecord', 'department_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Department']))

        # Changing field 'WorkRecord.position'
        db.alter_column(u'employees_workrecord', 'position_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['employees.Position']))

        # Changing field 'Employee.login'
        db.alter_column(u'employees_employee', 'login_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User']))

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
        u'employees.department': {
            'Meta': {'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'employees.employee': {
            'Meta': {'object_name': 'Employee'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'born': ('django.db.models.fields.DateField', [], {}),
            'card': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'login': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'on_delete': 'models.PROTECT'}),
            'patronymic': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'employees.position': {
            'Meta': {'object_name': 'Position'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'employees.visits': {
            'Meta': {'object_name': 'Visits'},
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Employee']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'employees.workrecord': {
            'Meta': {'object_name': 'WorkRecord'},
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Department']", 'on_delete': 'models.PROTECT'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Employee']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['employees.Position']", 'on_delete': 'models.PROTECT'})
        }
    }

    complete_apps = ['employees']