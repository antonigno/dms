#!/usr/bin/python
########################
# Calcola il rapporto percentuale tra RSS e VSZ dei processi 
# che hanno un nome identificato dalla variabile 'process_name'
# e l'utente dato dal comando 'whoami', utilizzando il comando 'ps'
# riporta un allarme se la percentuale supera la soglia definita
# nella variabile 'threshold'
########################
from __future__ import division
import shlex
import re
from subprocess import Popen, PIPE
from decimal import *

# variabili da configurare
process_name = 'java'
threshold = 90

# main
print "CONTROLLO MEMORIA DEI PROCESSI *%s*" %process_name
errors = []
(user, execution_errors) = Popen('/usr/ucb/whoami', stdout=PIPE, stderr=PIPE).communicate()
user = user.rstrip()
cmd = '/usr/bin/ps -eo pid,rss,vsz,user,comm'
args = shlex.split(cmd)
(output, execution_errors) = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
for line in output.splitlines():
    pattern = "\s+(?P<pid>\d+)\s+(?P<rss>\d+)\s+(?P<vsz>\d+)\s+%s\s+(?P<process>.*%s)" % (user, process_name)
    if re.search(pattern, line): 
	m = re.match(pattern, line)
	pid = int(m.group('pid'))
	rss = int(m.group('rss'))
	vsz = int(m.group('vsz'))
	process = m.group('process') 
	percent = Decimal(rss)/Decimal(vsz)*100
	print "%s, pid: %d percent: %.2f%%(RSS/VSZ)" % (process, pid, percent)
	if percent > threshold:
	    errors.append("ATTENZIONE: il processo %s con pid %d occupa %.2f%% di memoria" %(process, pid, percent)) 
print "ERRORI_CONTROLLO:"
for e in errors:
    print e

