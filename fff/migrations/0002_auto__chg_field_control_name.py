# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Control.name'
        db.alter_column('fff_control', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))

    def backwards(self, orm):

        # Changing field 'Control.name'
        db.alter_column('fff_control', 'name', self.gf('django.db.models.fields.CharField')(max_length=30))

    models = {
        'fff.area': {
            'Meta': {'object_name': 'Area'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'productionEnvironment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.ProductionEnvironment']"})
        },
        'fff.control': {
            'Meta': {'unique_together': "(('name', 'script', 'time_slot'),)", 'object_name': 'Control'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'productionEnvironment': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fff.ProductionEnvironment']", 'null': 'True', 'symmetrical': 'False'}),
            'script': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'threshold': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time_slot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.TimeSlot']"})
        },
        'fff.controlstatus': {
            'Meta': {'object_name': 'ControlStatus', 'managed': 'False'},
            'control': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.Control']"}),
            'control_time': ('django.db.models.fields.DateTimeField', [], {}),
            'errors': ('django.db.models.fields.CharField', [], {'max_length': '6000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output': ('django.db.models.fields.CharField', [], {'max_length': '6000'}),
            'productionEnvironment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.ProductionEnvironment']"})
        },
        'fff.executedcontrol': {
            'Meta': {'unique_together': "(('control', 'control_time'),)", 'object_name': 'ExecutedControl'},
            'control': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.Control']"}),
            'control_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'errors': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output': ('django.db.models.fields.TextField', [], {})
        },
        'fff.fileserve': {
            'Meta': {'unique_together': "(('file_name', 'file_path', 'destination_path', 'productionEnvironment'),)", 'object_name': 'FileServe'},
            'destination_path': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permissions': ('django.db.models.fields.CharField', [], {'default': "'644'", 'max_length': '3'}),
            'productionEnvironment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.ProductionEnvironment']"})
        },
        'fff.host': {
            'Meta': {'object_name': 'Host'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'fff.productionenvironment': {
            'Meta': {'unique_together': "(('host', 'user'),)", 'object_name': 'ProductionEnvironment'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.User']"})
        },
        'fff.statistic': {
            'Meta': {'unique_together': "(('stat_time', 'stat_element', 'productionEnvironment'),)", 'object_name': 'Statistic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'productionEnvironment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.ProductionEnvironment']"}),
            'statType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fff.StatType']"}),
            'stat_element': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'stat_extra': ('django.db.models.fields.TextField', [], {}),
            'stat_time': ('django.db.models.fields.DateTimeField', [], {}),
            'stat_value': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'fff.stattype': {
            'Meta': {'object_name': 'StatType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'fff.timeslot': {
            'Meta': {'unique_together': "(('start_time', 'end_time'),)", 'object_name': 'TimeSlot'},
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'fff.user': {
            'Meta': {'object_name': 'User'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'primary_key': 'True'})
        }
    }

    complete_apps = ['fff']