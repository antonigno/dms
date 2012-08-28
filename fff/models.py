'''
author: Borgia Antonino Stefano
mail: stefano.borgia@gmail.com
django model classes
'''

from django.db import models
from django import forms
from django.forms import ModelForm, ModelChoiceField
from utils import QuerySetChain


class Host(models.Model):
    '''Hostnames and relative IPs'''
    name = models.CharField(max_length=30, unique=True)
    ip = models.CharField(max_length=16)

    def __unicode__(self):
        return "%s-%s" % (self.name, self.ip)


class User(models.Model):
    '''Usernames'''
    name = models.CharField(max_length=30, unique=True, primary_key=True)

    def __unicode__(self):
        return "%s" % (self.name)


class ProductionEnvironment(models.Model):
    '''Logic association between Hosts and Users'''
    name = models.CharField(max_length=30)
    host = models.ForeignKey(Host)
    user = models.ForeignKey(User)
    active = models.BooleanField(default=False)

    class Meta:
        '''model meta class'''
        unique_together = (('host', 'user'),)

    def __unicode__(self):
        return "%s (%s %s) active:%s" % (self.name, self.host, self.user, self.active)


class Area(models.Model):
    '''Logic association between ProductionEnvironments'''
    name = models.CharField(max_length=30)
    productionEnvironment = models.ForeignKey(ProductionEnvironment)

    def __unicode__(self):
        return "%s" % self.name


class TimeSlot(models.Model):
    '''
    Start time - End time.
    Used to deliver list of Controls to be executed on PEs
    '''
    # TODO: inserire se serve la granularita' (es. ogni 5 min)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('start_time', 'end_time', )

    def __unicode__(self):
        return "%s - %s" % (self.start_time, self.end_time)


class Control(models.Model):
    '''Control executed on PEs'''
    name = models.CharField(max_length=50)
    productionEnvironment = models.ManyToManyField(ProductionEnvironment, null=True)
    script = models.CharField(max_length=50)
    time_slot = models.ForeignKey(TimeSlot)
    threshold = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('name', 'script', 'time_slot', )

    def __unicode__(self):
        return "%s:  (%s - %s)" % (self.name, self.script, self.time_slot)


class FileServe(models.Model):
    '''List of pointers to files to be sent to PEs'''
    file_name = models.CharField(max_length=50)
    file_path = models.CharField(max_length=50)
    destination_path = models.CharField(max_length=50)
    productionEnvironment = models.ForeignKey(ProductionEnvironment)
    permissions = models.CharField(max_length=3, default="644")
    error = models.BooleanField()

    class Meta:
        '''model meta class'''
        unique_together = (('file_name', 'file_path', \
                                'destination_path', \
                                'productionEnvironment'), )

    def __unicode__(self):
        return "%s/%s" % (self.file_path, self.file_name)


class ControlStatus(models.Model):
    '''
    model derived from a memory table with
    last executions of all controls
    '''
    id = models.AutoField(primary_key=True)
    control = models.ForeignKey(Control)
    output = models.CharField(max_length=6000)
    errors = models.CharField(max_length=6000, blank=True)
    control_time = models.DateTimeField()
    productionEnvironment = models.ForeignKey(ProductionEnvironment)

    class Meta:
        db_table = u'fff_controlstatus'
        managed = False

    def __unicode__(self):
        return "%s - %s - %s" % (self.productionEnvironment, \
                                 self.control_time, self.control.name)


class ExecutedControl(models.Model):
    '''History of all Control executions'''
    control = models.ForeignKey(Control)
    output = models.TextField()
    errors = models.TextField(blank=True, null=True)
    control_time = models.DateTimeField(auto_now=True)

    class Meta:
        '''model meta class'''
        unique_together = (('control', 'control_time'), )

    def __unicode__(self):
        return "%s %s %s" % (\
            self.control.productionEnvironment, \
                self.control_time, self.control.name)


class StatType(models.Model):
    '''Type of statistics (e.g. file system, error)'''
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return "%s" % (self.name)


class Statistic(models.Model):
    '''Structurated data coming from PEs,
    with helper classes for queries, graphs...'''
    stat_time = models.DateTimeField(auto_now=False)
    timestamp = models.DateTimeField(auto_now=False, blank=True, null=True)
    stat_element = models.CharField(max_length=300)
    stat_value = models.IntegerField()
    stat_extra = models.TextField()
    productionEnvironment = models.ForeignKey(ProductionEnvironment)
    statType = models.ForeignKey(StatType)
    # BUG Ticket #2495: https://code.djangoproject.com/ticket/2495
    # non si puo' mettere unique a un campo text se il backend e' mysql
    # per risolvere ho messo un CharField al posto di un
    # TextField nel campo stat_element
    #class Meta:
    #    '''model meta class'''
    #    unique_together = (('stat_time', 'stat_element', 'productionEnvironment', 'statType',), )

    def __unicode__(self):
        return "%s-%s-%s" % (self.stat_element, \
                                 self.stat_time, self.productionEnvironment)

