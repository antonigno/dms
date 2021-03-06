'''
author: Borgia Antonino Stefano
mail: antonino.borgia@guest.telecomitalia.it

django view classes
'''

import sys
import re
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.template import RequestContext, loader
from django import forms
from django.forms.widgets import SelectMultiple
from django.views.decorators.csrf import csrf_protect
from models import Control, ProductionEnvironment, Area, TimeSlot, FileServe
from models import Statistic
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
import logging
from django.db.models import Q
import datetime
from django.utils import simplejson
from django.core import serializers

LOGGER = logging.getLogger('logview.outlog')


def index(request):
    '''main view'''
    tmpl = loader.get_template('fff/index.html')
    return HttpResponse(tmpl.render(RequestContext(request)))


def file_serve_list(request):
    '''
    view for file serve list management
    '''
    fs_list = FileServe.objects.all()
    tmpl = loader.get_template('fff/file_serve_list.html')
    if request.method == 'POST':  # If the form has been submitted...
        form = FileServeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except:
                message = "Unexpected error:%s" % sys.exc_info()[0]
                LOGGER.error(message)
                form = FileServeForm()
                context = RequestContext(request, {
                        'file_serve_list': fs_list,
                        'form': form,
                        })
                return HttpResponse(tmpl.render(context))
        else:
            # TODO inserire un errore a schermo
            context = RequestContext(request, {
                        'file_serve_list': fs_list,
                        'form': form,
                        })
            LOGGER.error(form.errors)
            LOGGER.error("non validato")
    #else:
    form = FileServeForm()
    context = RequestContext(request, {
    'file_serve_list': fs_list,
    'form': form,
    })
    return HttpResponse(tmpl.render(context))


def file_serve_delete(request):
    '''file_serve deleting view'''
    data = request.POST
    file_name = data['file_name']
    file_path = data['file_path']
    destination_path = data['destination_path']
    pe_name = data['production_environment']
    LOGGER.info("cancello il file %s%s destination %s pe %s" \
% (file_path, file_name, destination_path, data['production_environment']))
    # il nome del productionEnvironment potrebbe non essere unico,
    # mentre lo e' il nome del relativo host
    file_serve = FileServe.objects.filter(file_name=file_name, \
file_path=file_path, destination_path=destination_path, \
productionEnvironment__host__name=pe_name)
    file_serve[0].delete()
    request.POST = None
    return file_serve_list(request)


def area_list(request):
    '''area list managing view'''
    a_list = Area.objects.all()
    tmpl = loader.get_template('fff/area_list.html')
    if request.method == 'POST':  # If the form has been submitted...
        form = AreaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except:
                LOGGER.error("Unexpected error:", sys.exc_info()[0])
                form = AreaForm()
                context = RequestContext(request, {
                        'area_list': a_list,
                        'form': form,
                        })
                return HttpResponse(tmpl.render(context))
        else:
            # TODO inserire un errore a schermo
            LOGGER.error(form.errors)
            LOGGER.error("non validato")
    else:
        form = AreaForm()
    context = RequestContext(request, {
            'area_list': a_list,
            'form': form,
            })
    return HttpResponse(tmpl.render(context))


def control_list(request, dest='area'):
    '''control list managing view'''
    c_list = Control.objects.all().order_by('name')
    tmpl = loader.get_template('fff/control_list.html')
    if request.method == 'POST':  # If the form has been submitted...
        form = ControlForm(dest, request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            for pes in form.cleaned_data['host']:
                LOGGER.debug(pes)
            try:
                form.save()
            except:
                LOGGER.error("Unexpected error:", sys.exc_info()[0])
                form = ControlForm(dest)
                context = RequestContext(request, {
                        'control_list': c_list,
                        'form': form,
                        'error_message': "Controllo gia' inserito.",
                        'dest': dest,
                        })
                return HttpResponse(tmpl.render(context))
        else:
            # TODO inserire un errore a schermo
            LOGGER.error("non validato:%s" % request.POST)
    else:
        form = ControlForm(dest)
    context = RequestContext(request, {
            'control_list': c_list,
            'form': form,
            'dest': dest,
            })
    return HttpResponse(tmpl.render(context))


def control_list_delete(request):
    '''control list deleting view'''
    data = request.POST
    name = data['name']
    hostname = data['hostname']
    user = data['user']
    script = data['script']
    match = re.match(r"(?P<start_time>\d{2}:\d{2}:\d{2}) - (?P<end_time>\d{2}:\d{2}:\d{2})", data['time_slot'])
    start_time = match.group('start_time')
    end_time = match.group('end_time')
    LOGGER.info("rimuovo il controllo %s su %s@%s" % (name, user, hostname))
    control = Control.objects.filter(name=name, script=script, \
time_slot__start_time=start_time, time_slot__end_time=end_time)
    try:
        control[0].productionEnvironment.clear()
        control[0].delete()
    except IndexError:
        LOGGER.error("controllo %s %s@%s non esistente" \
% (name, user, hostname))
    request.POST = None
    return control_list(request)


#@csrf_protect
#def allinea_file(request):
#    '''lista di file da allineare DEPRECATED'''
#    lista = Allinea_file.objects.all()
#    tmpl = loader.get_template('fff/allinea_file.html')
#    if request.method == 'POST':  # If the form has been submitted...
#        form = AllineaFileForm(request.POST)  # A form bound to the POST data
#        if form.is_valid():  # All validation rules pass
#            user = form.cleaned_data['user']
#            hosts = form.cleaned_data['host']
#            nome_file = form.cleaned_data['file']
#            destination_path = form.cleaned_data['destination_path']
#            repository = form.cleaned_data['repository']
#            repository_user = form.cleaned_data['repository_user']
#            for host in hosts:
#                try:
#                    file_da_allineare(host, user, \
#nome_file, destination_path, repository, repository_user)
#                except IntegrityError:
#                    #TODO messaggio d'errore dell'eccezione (duplicate entry)
#                    form = AllineaFileForm()
#                    context = RequestContext(request, {
#                            'lista_file': lista,
#                            'form': form,
#                            'error_message': "File %s gia' inserito per la \
#macchina %s@%s" % (nome_file, user, host),
#                            })
#                    return HttpResponse(tmpl.render(context))
#        else:
#            # TODO inserire un errore a schermo
#            LOGGER.error("non validato")
#    else:
#        form = AllineaFileForm()
#    context = RequestContext(request, {
#            'lista_file': lista,
#            'form': form,
#            })
#    return HttpResponse(tmpl.render(context))


#def file_da_allineare(host, user, nome_file, destination_path, \
#repository, repository_user):
#    '''lista di file da allineare DEPRECATED'''
#    #print "cerco macchina %s e repository %s"  %(host, repository)
#    macchina = Macchine.objects.get(hostname=host)
#    utenza = Utenze_Applicative.objects.get(utenza=user)
#    repo = Macchine.objects.get(hostname=repository)
#    repo_user = Utenze_Applicative.objects.get(utenza=repository_user)
#    afile = Allinea_file(host=macchina, user=utenza, nome_file=nome_file, \
#destination_path=destination_path, repository=repo, repository_user=repo_user)
#    try:
#        afile.save()
#    except IntegrityError:
#        raise


#@csrf_protect
#def file_allineato(request):
#    '''risultato allineamento DEPRECATED'''
#    f_all = get_object_or_404(Allinea_file, id=request.POST["file_id"])
#    f_all.delete()
#    lista = Allinea_file.objects.all()
#    tmpl = loader.get_template('fff/allinea_file.html')
#    form = AllineaFileForm()
#    context = RequestContext(request, {
#            'lista_file': lista,
#            'form': form,
#            })
#    return HttpResponse(tmpl.render(context))


#class AllineaFileForm(forms.forms.Form):
#    '''form per allineamento file DEPRECATED'''
#    host_choices = [(m.hostname, m.hostname) for m in Macchine.objects.all()]
#    user_choices = [(u.utenza, u.utenza) \
#for u in Utenze_Applicative.objects.all()]
#    host = forms.MultipleChoiceField(widget=SelectMultiple, \
#choices=host_choices)
#    user = forms.ChoiceField(choices=user_choices)
#    destination_path = forms.CharField(max_length=50)
#    file = forms.CharField(max_length=50)
#    repository = forms.ChoiceField(choices=host_choices)
#    repository_user = forms.ChoiceField(choices=user_choices)


class FileServeForm(forms.forms.Form):
    '''Form for inserting new file serve entries'''
    PE_choices = []
    file_name = forms.CharField(max_length=50)
    file_path = forms.CharField(max_length=50, required=False)
    destination_path = forms.CharField(max_length=50, required=False)
    production_environment = forms.MultipleChoiceField(\
widget=SelectMultiple(attrs={'size': 10, }), choices=PE_choices)
    permissions = forms.CharField(max_length=3, required=False)
    error = forms.BooleanField(required=False)
    # serve per permettere il caricamento automatico delle choices,
    # altrimenti avviene solo al momento dell' instanziamento
    # vedi: http://djangosnippets.org/snippets/26/

    def __init__(self, *args, **kwargs):
        super(FileServeForm, self).__init__(*args, **kwargs)
        self.fields['production_environment'].choices = \
[((pe.host.name), "%s (%s)" % (pe.name, pe.host)) \
for pe in ProductionEnvironment.objects.all().order_by("host__name")]

    def save(self):
        '''Save entry in DB'''
        data = self.cleaned_data
        file_name = data['file_name']
        file_path = data['file_path']
        destination_path = data['destination_path']
        permissions = data['permissions']
        error = data['error']
        LOGGER.debug(data['production_environment'])
        for host_name in data['production_environment']:
            pes = ProductionEnvironment.objects.filter(host__name=host_name)
            # diversi pe possono avere lo stesso nome (eg.grte1,grte2->grte)
            for prod_env in pes:
                file_serve = FileServe(file_name=file_name, \
file_path=file_path, destination_path=destination_path, \
productionEnvironment=prod_env, permissions=permissions, error=error)
                file_serve.save()


class AreaForm(forms.forms.Form):
    '''Form for inserting new Area entries'''
    name = forms.CharField(max_length=50)
    PE_choices = []
    production_environment = forms.MultipleChoiceField(\
widget=SelectMultiple(attrs={'size': 10, }), choices=PE_choices)
    # serve per permettere il caricamento automatico delle choices,
    # altrimenti avviene solo al momento dell' instanziamento
    # vedi: http://djangosnippets.org/snippets/26/

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        self.fields['production_environment'].choices = [\
(pe.name, pe.name) for pe in ProductionEnvironment.objects.all()]

    def save(self):
        '''Save entry in db'''
        data = self.cleaned_data
        name = data['name']
        for pe_name in data['production_environment']:
            prod_env = ProductionEnvironment.objects.filter(name=pe_name)
            area = Area(name=name, productionEnvironment=prod_env[0])
            area.save()


class ControlForm(forms.forms.Form):
    '''Form for inserting new Control entries'''
    name = forms.CharField(max_length=50)
    host = forms.MultipleChoiceField(\
widget=SelectMultiple(attrs={'size': 10, }), choices=[('', '')])
    script = forms.CharField(\
max_length=50, help_text='path relativo al client')
    time_slot = forms.ChoiceField(\
choices=[(ts, "%s - %s" % (ts.start_time, ts.end_time)) \
for ts in TimeSlot.objects.all()])

    def __init__(self, dest, *args):
        self.dest = dest
        if self.dest == 'host':
            attrs = {'size': 10, }
            choices = [(pe, "%s" % pe) \
for pe in ProductionEnvironment.objects.values_list('name', flat=True)\
.order_by('name').distinct()]
        elif self.dest == 'area':
            attrs = {'size': 5, }
            choices = [(a, "%s" % a) \
for a in Area.objects.values_list('name', flat=True).distinct()]
        else:
            attrs = {'size': 10, }
            choices = [(pe, "%s (%s, %s)" % (pe.name, pe.host.name, pe.user.name)) for pe in \
ProductionEnvironment.objects.all().order_by("host__name").distinct('name')]
            LOGGER.error("dest %s not available" % self.dest)
        super(ControlForm, self).__init__(*args)
        self.fields['host'].widget = SelectMultiple(attrs=attrs)
        self.fields['host'].choices = choices

    def save(self):
        '''Save entry in DB'''
        data = self.cleaned_data
        LOGGER.debug(data)
        name = data['name']
        script = data['script']
        match = re.match(r'(?P<start>\d{2}:\d{2}:\d{2}) - (?P<end>\d{2}:\d{2}:\d{2})', data['time_slot'])
        time_slot = TimeSlot.objects.filter(\
start_time=match.group('start'), end_time=match.group('end'))
        control = Control(name=name, script=script, time_slot=time_slot[0])
        control.save()
        if self.dest == 'host':
            for host in data['host']:
                # match = re.match(r'(?P<pe_name>\w+) .*', h)
                # pe_name = match.group('pe_name')
                pes = ProductionEnvironment.objects.filter(name=host)
        elif self.dest == 'area':
            for area in data['host']:
                LOGGER.debug("salvo area %s" % area)
                pes = [area.productionEnvironment \
for area in Area.objects.filter(name=area)]
        for prod_env in pes:
            prod_env.control_set.add(control)




######
# le seguenti classi sono dei test
# cancellare eventualmente

#def select_stat(request):
    
def andamento_batch(request):
    callback = request.GET['callback']
    print "CALLBACK: %s" % callback
    from collections import defaultdict
    days = {}
    batch = {}
    batches = []
    one_month = datetime.timedelta(days=31)
    one_week = datetime.timedelta(days=7)
#select stat_time, stat_value from fff_statistic where stat_element like 'extend_CLASSIC%' or stat_element like 'renew_CLASSIC%';
#    stats = Statistic.objects.filter( Q(stat_element__startswith = 'extend_CLASSIC') | Q(stat_element__startswith = 'renew_CLASSIC'), Q(stat_time__gt = (datetime.datetime.today()- one_month) ))
    # un mese
    # stats = Statistic.objects.filter( Q(stat_element__endswith = '_CLASSIC'), Q(stat_time__gt = (datetime.datetime.today() - one_month)))
    # 15 giorni
    stats = Statistic.objects.filter( Q(stat_element__endswith = '_CLASSIC'), Q(stat_time__gt = (datetime.datetime.today() - one_week*8)))

    json_batches = serializers.serialize('json', stats, fields=('stat_element', 'stat_value','stat_time'))

    # for stat in stats:
    #     k = stat.stat_time.date().strftime("%Y%m%d")
    #     days[k] = days.get(k, 0) + stat.stat_value

    # for day in days:
    #     batch = {}
    #     batch['type'] = 'CLASSIC'
    #     batch['day'] = day
    #     batch['value'] = days[day]
    #     batches.append(batch)

#    tmpl = loader.get_template('fff/andamento_batch.html')
#    context = RequestContext(request, {
#            'stats': batches,
#            'lista_file': lista,
#            'form': form,
#            })
#    return HttpResponse(tmpl.render(context))
    #return  HttpResponse(simplejson.dumps(batches), mimetype="application/json")
    #return  HttpResponse(simplejson.dumps(batches), mimetype='application/javascript')

    aaa = '[{"type": "CLASSIC", "day": "120429", "value": 2715476}, {"type": "CLASSIC", "day": "120428", "value": 2989100}, {"type": "CLASSIC", "day": "120421", "value": 2974475}, {"type": "CLASSIC", "day": "120420", "value": 2888642}, {"type": "CLASSIC", "day": "120423", "value": 2469508}, {"type": "CLASSIC", "day": "120422", "value": 2684326}, {"type": "CLASSIC", "day": "120425", "value": 2863271}, {"type": "CLASSIC", "day": "120424", "value": 2806356}, {"type": "CLASSIC", "day": "120427", "value": 2958198}, {"type": "CLASSIC", "day": "120426", "value": 2910617}, {"type": "CLASSIC", "day": "120414", "value": 2849220}, {"type": "CLASSIC", "day": "120415", "value": 2578786}, {"type": "CLASSIC", "day": "120416", "value": 2377632}, {"type": "CLASSIC", "day": "120417", "value": 2736412}, {"type": "CLASSIC", "day": "120410", "value": 2662523}, {"type": "CLASSIC", "day": "120411", "value": 2734848}, {"type": "CLASSIC", "day": "120412", "value": 2722505}, {"type": "CLASSIC", "day": "120413", "value": 2779762}, {"type": "CLASSIC", "day": "120418", "value": 2854711}, {"type": "CLASSIC", "day": "120419", "value": 2842430}, {"type": "CLASSIC", "day": "120502", "value": 2887590}, {"type": "CLASSIC", "day": "120501", "value": 3810841}, {"type": "CLASSIC", "day": "120506", "value": 2623720}, {"type": "CLASSIC", "day": "120430", "value": 2445573}, {"type": "CLASSIC", "day": "120505", "value": 2894875}, {"type": "CLASSIC", "day": "120409", "value": 0}]'

    return HttpResponse('%s([{"pk": 278272, "model": "fff.statistic", "fields": {"stat_time": "2012-05-05 00:00:00", "stat_value": 0, "stat_element": "deact_acc_CLASSIC"}}, {"pk": 278560, "model": "fff.statistic", "fields": {"stat_time": "2012-05-05 03:00:00", "stat_value": 100, "stat_element": "deact_off_CLASSIC"}}])' % callback)


    return HttpResponse('Ext.data.JsonP.callback1([{"pk": 278272, "model": "fff.statistic", "fields": [{"stat_time": "2012-05-05 00:00:00", "stat_value": 0, "stat_element": "deact_acc_CLASSIC"}]}, {"pk": 278560, "model": "fff.statistic", "fields": [{"stat_time": "2012-05-05 01:00:00", "stat_value": 100, "stat_element": "deact_off_CLASSIC"}]}])')

    # return HttpResponse('Ext.data.JsonP.callback1(%s)' % simplejson.dumps(batches))
    return HttpResponse('Ext.data.JsonP.callback1(%s)' % json_batches)
