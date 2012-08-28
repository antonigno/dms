# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Host'
        db.create_table('fff_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('fff', ['Host'])

        # Adding model 'User'
        db.create_table('fff_user', (
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30, primary_key=True)),
        ))
        db.send_create_signal('fff', ['User'])

        # Adding model 'ProductionEnvironment'
        db.create_table('fff_productionenvironment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.Host'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.User'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('fff', ['ProductionEnvironment'])

        # Adding unique constraint on 'ProductionEnvironment', fields ['host', 'user']
        db.create_unique('fff_productionenvironment', ['host_id', 'user_id'])

        # Adding model 'Area'
        db.create_table('fff_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('productionEnvironment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.ProductionEnvironment'])),
        ))
        db.send_create_signal('fff', ['Area'])

        # Adding model 'TimeSlot'
        db.create_table('fff_timeslot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('fff', ['TimeSlot'])

        # Adding unique constraint on 'TimeSlot', fields ['start_time', 'end_time']
        db.create_unique('fff_timeslot', ['start_time', 'end_time'])

        # Adding model 'Control'
        db.create_table('fff_control', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('script', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('time_slot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.TimeSlot'])),
            ('threshold', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('fff', ['Control'])

        # Adding unique constraint on 'Control', fields ['name', 'script', 'time_slot']
        db.create_unique('fff_control', ['name', 'script', 'time_slot_id'])

        # Adding M2M table for field productionEnvironment on 'Control'
        db.create_table('fff_control_productionEnvironment', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('control', models.ForeignKey(orm['fff.control'], null=False)),
            ('productionenvironment', models.ForeignKey(orm['fff.productionenvironment'], null=False))
        ))
        db.create_unique('fff_control_productionEnvironment', ['control_id', 'productionenvironment_id'])

        # Adding model 'FileServe'
        db.create_table('fff_fileserve', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('file_path', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('destination_path', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('productionEnvironment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.ProductionEnvironment'])),
            ('permissions', self.gf('django.db.models.fields.CharField')(default='644', max_length=3)),
            ('error', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('fff', ['FileServe'])

        # Adding unique constraint on 'FileServe', fields ['file_name', 'file_path', 'destination_path', 'productionEnvironment']
        db.create_unique('fff_fileserve', ['file_name', 'file_path', 'destination_path', 'productionEnvironment_id'])

        # Adding model 'ExecutedControl'
        db.create_table('fff_executedcontrol', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('control', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.Control'])),
            ('output', self.gf('django.db.models.fields.TextField')()),
            ('errors', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('control_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('fff', ['ExecutedControl'])

        # Adding unique constraint on 'ExecutedControl', fields ['control', 'control_time']
        db.create_unique('fff_executedcontrol', ['control_id', 'control_time'])

        # Adding model 'StatType'
        db.create_table('fff_stattype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('fff', ['StatType'])

        # Adding model 'Statistic'
        db.create_table('fff_statistic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stat_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('stat_element', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('stat_value', self.gf('django.db.models.fields.IntegerField')()),
            ('stat_extra', self.gf('django.db.models.fields.TextField')()),
            ('productionEnvironment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.ProductionEnvironment'])),
            ('statType', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fff.StatType'])),
        ))
        db.send_create_signal('fff', ['Statistic'])

        # Adding unique constraint on 'Statistic', fields ['stat_time', 'stat_element', 'productionEnvironment']
        db.create_unique('fff_statistic', ['stat_time', 'stat_element', 'productionEnvironment_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Statistic', fields ['stat_time', 'stat_element', 'productionEnvironment']
        db.delete_unique('fff_statistic', ['stat_time', 'stat_element', 'productionEnvironment_id'])

        # Removing unique constraint on 'ExecutedControl', fields ['control', 'control_time']
        db.delete_unique('fff_executedcontrol', ['control_id', 'control_time'])

        # Removing unique constraint on 'FileServe', fields ['file_name', 'file_path', 'destination_path', 'productionEnvironment']
        db.delete_unique('fff_fileserve', ['file_name', 'file_path', 'destination_path', 'productionEnvironment_id'])

        # Removing unique constraint on 'Control', fields ['name', 'script', 'time_slot']
        db.delete_unique('fff_control', ['name', 'script', 'time_slot_id'])

        # Removing unique constraint on 'TimeSlot', fields ['start_time', 'end_time']
        db.delete_unique('fff_timeslot', ['start_time', 'end_time'])

        # Removing unique constraint on 'ProductionEnvironment', fields ['host', 'user']
        db.delete_unique('fff_productionenvironment', ['host_id', 'user_id'])

        # Deleting model 'Host'
        db.delete_table('fff_host')

        # Deleting model 'User'
        db.delete_table('fff_user')

        # Deleting model 'ProductionEnvironment'
        db.delete_table('fff_productionenvironment')

        # Deleting model 'Area'
        db.delete_table('fff_area')

        # Deleting model 'TimeSlot'
        db.delete_table('fff_timeslot')

        # Deleting model 'Control'
        db.delete_table('fff_control')

        # Removing M2M table for field productionEnvironment on 'Control'
        db.delete_table('fff_control_productionEnvironment')

        # Deleting model 'FileServe'
        db.delete_table('fff_fileserve')

        # Deleting model 'ExecutedControl'
        db.delete_table('fff_executedcontrol')

        # Deleting model 'StatType'
        db.delete_table('fff_stattype')

        # Deleting model 'Statistic'
        db.delete_table('fff_statistic')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
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