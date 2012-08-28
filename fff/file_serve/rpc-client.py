#!/usr/bin/python
import xmlrpclib
from subprocess import Popen, PIPE
import shlex
from datetime import datetime
import getpass
import socket
import unittest
import string
import getopt
import sys
import os
import logging
import re
from exceptions import OSError

def parse_output(complete_output, separator_list, offset=""):
    '''
    given a multiline string returns a dictionary of substrings, 
    one per separator given and with separator as key, plus the initial string 
    starting from passed offset returned with special key 'first'
    >>> parse_output("output controllo\nERRORI_CONTROLLO:\nerrori controllo\nINFO_LINK:\ninfo link controllo\nSTATISTICHE:\n###",("ERRORI_CONTROLLO:\n","INFO_LINK:\n", "STATISTICHE:\n", "STATISTICHE:\n",))
    {'first': 'output controllo\n', 'INFO_LINK:': 'info link controllo', 'ERRORI_CONTROLLO:': 'errori controllo\n', 'STATISTICHE:': 'stats',}
    '''
    off_flag = 0
    fields = {}
    remaining = complete_output
    for separator in reversed(separator_list):
        remaining_fields = remaining.split(separator)
        if len(remaining_fields) > 1:
            fields[separator.rstrip()] = remaining_fields.pop().lstrip()
        else:
            fields[separator.rstrip()] = ""
        remaining = ''.join(remaining_fields)
    if offset:
        fields['first'] = remaining.split(offset).pop()
    else:
        fields['first'] = remaining
    for key in fields.keys():
	fields[key] = reduce(''.join(fields[key]))
    return fields


def reduce(stringToReduce, lineNumbers = 30):
    '''
    receives a string and returns a list reduced to lineNumbers size 
    '''
    if lineNumbers < 30:
        lineNumbers = 30 
    lines = stringToReduce.splitlines(True)
    #lines = stringToReduce
    reducedLines = []
    size = len(lines)
    if size > lineNumbers:
        for i in range(lineNumbers - 5):
            reducedLines.append(lines[i])
        reducedLines.append("[...]\naltre %s linee\n[...]\n" %(size - lineNumbers))
        for j in reversed(range(1,10)):
            ind = size - j
            reducedLines.append(lines[ind])
        return ''.join(reducedLines)
    else:
        return ''.join(lines)
        


def parse_stats(stats):
    stat_list = []
    lines = re.split(r'\n', stats)
    for line in lines:
	stat = re.split(r'###', line)
	if len(stat) == 8:
	    stat_dict = {}
	    stat_dict['host'] = stat[0]
	    stat_dict['user'] = stat[1]
	    stat_dict['stat_value'] = stat[2]
	    stat_dict['stat_time'] = stat[3]
	    stat_dict['stat_element'] = stat[4]
	    stat_dict['timestamp'] = stat[5]
	    stat_dict['extra'] = stat[6]
	    stat_dict['stat_type'] = stat[7]
	    stat_list.append(stat_dict)
    return stat_list


def main():
    logging.basicConfig(filename='rpc-client.log',level=logging.DEBUG)
    # get current username and hostname
    user = getpass.getuser()
    host = socket.gethostname()

    # Print list of available methods
    #print s.system.listMethods()
    
    print "Richiedo la lista di controlli da eseguire."
	
    try:
        # connect to the server
        s = xmlrpclib.ServerProxy('http://10.41.8.85:8000')
        lista_controlli = s.lista_controlli({'host':host, 'user':user})
	logging.debug(lista_controlli)
	print lista_controlli
    except xmlrpclib.Fault, err:
        #print sys.exc_info()
        logging.error("A fault occurred")
        logging.error("Fault code: %d" % err.faultCode)
        logging.error("Fault string: %s" % err.faultString)
    lista_output = []
    complete_output = ""
    for controllo in lista_controlli:
        script = controllo['script']
        logging.debug("Invio controllo: %s (%s)" % (controllo['nome_controllo'], script))
        args = shlex.split(script)
        try:
            (complete_output, errori_esecuzione) = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
            fields = parse_output(complete_output,("ERRORI_CONTROLLO:", "INFO_LINK:", "STATISTICHE:"), "")
            output = fields['first']
            errori = fields.get('ERRORI_CONTROLLO:','')
            info_link = fields.get('INFO_LINK:','')
	    stat_fields = fields.get('STATISTICHE:','')
	    stats = parse_stats(stat_fields);
            ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.debug(ora)  
	    lista_output.append({'host': host, 'user': user, 'nome_controllo':controllo['nome_controllo'], 'output':xmlrpclib.Binary(output), 'errori': xmlrpclib.Binary(errori), 'errori_esecuzione':errori_esecuzione, 'ora': ora, 'script':script, 'stats':stats})
        except OSError:
            logging.error("Unexpected error:", sys.exc_info()[0])
            errori_esecuzione = sys.exc_info()[1]
            print errori_esecuzione
            pass

    if len(lista_output) > 0:
        try:
            print s.esito_controllo_bulk(lista_output)
        except xmlrpclib.Fault, err:
            print "A fault occurred"
            print "Fault code: %d" % err.faultCode
            print "Fault string: %s" % err.faultString
    print "Controllo eventuali file da allineare."
    try:
        for f in s.file_align({'host':host, 'user':user}):
            print f
            filename = f['file_name']
	    destination_path = "%s/%s" %(os.getcwd(),f['destination_path'])
            fullpath = "%s/%s/%s" %(os.getcwd(),f['destination_path'], filename)
            try:
		#d = os.path.dirname(destination_path)
		#print os.path.isdir(destination_path)
		if not os.path.isdir(destination_path):
		    print "creating directory %s" % destination_path
		    os.mkdir(destination_path)
                handle = open(fullpath, 'wb')
                handle.write(f['file'].data)
                handle.close()
                # devo convertire la stringa in ottale per chmod
                perm = int("0"+f['permissions'],8)
                os.chmod(fullpath,perm)
                print "File %s allineato." %filename
                print "Effettuo un ack per il %s " %filename 
                print s.file_align({'host':host, 'user':user, 'ack':filename})
            except IOError:
                print sys.exc_info()[1]
                print s.file_align({'host':host, 'user':user, 'ack':filename, 'excecution_errors':'IOError'})
    except xmlrpclib.Fault, err:
        print "A fault occurred"
        print "Fault code: %d" % err.faultCode
        print "Fault string: %s" % err.faultString

        
class TestClientFunctions(unittest.TestCase):
    def test_parse_output(self):
        fields = parse_output("output controllo\nERRORI_CONTROLLO:\nerrori controllo\nINFO_LINK:\ninfo link controllo",("ERRORI_CONTROLLO:","INFO_LINK:"))
        self.assertEqual(fields['first'],"output controllo\n")
        self.assertEqual(fields['ERRORI_CONTROLLO:'],"errori controllo\n")
        self.assertEqual(fields['INFO_LINK:'],'info link controllo')

    def test_parse_output_with_offset(self):
        fields = parse_output("output controllo\nERRORI_CONTROLLO:\nerrori controllo\nINFO_LINK:\ninfo link controllo",("ERRORI_CONTROLLO:","INFO_LINK:"),"output")
        self.assertEqual(fields['first']," controllo\n")

    def test_parse_output_ls(self):
        (complete_output, errori_esecuzione) = Popen('ls', stdout=PIPE, stderr=PIPE).communicate()
        fields = parse_output(complete_output,("ERRORI_CONTROLLO:","INFO_LINK:"),"" )
        self.assertEqual(fields['ERRORI_CONTROLLO:'],"")
        self.assertEqual(fields['INFO_LINK:'],"")
    

def usage():
    print "python rpc-client.py [-t|--test], -t effettua solamente le operazioni di testing"


if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "t", "test")
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    test = False
    for o, a in optlist:
        if o in ("-t", "--test"):
            test = True
    if test:
        print "Unit test start:"
        del sys.argv[1:]
        unittest.main()
        sys.exit(1)
    main()
