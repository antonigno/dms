# utility condivise
import datetime
import re
import logging

logger = logging.getLogger('logview.outlog')



class QuerySetChain(object):
    """
    Chains multiple subquerysets (possibly of different models) and behaves as
    one queryset.  Supports minimal methods needed for use with
    django.core.paginator.
    """

    def __init__(self, *subquerysets):
        self.querysets = subquerysets

    def count(self):
        """
        Performs a .count() for all subquerysets and returns the number of
        records as an integer.
        """
        return sum(qs.count() for qs in self.querysets)

    def _clone(self):
        "Returns a clone of this queryset chain"
        return self.__class__(*self.querysets)

    def _all(self):
        "Iterates records in all subquerysets"
        return chain(*self.querysets)

    def __getitem__(self, ndx):
        """
        Retrieves an item or slice from the chained set of results from all
        subquerysets.
        """
        if type(ndx) is slice:
            return list(islice(self._all(), ndx.start, ndx.stop, ndx.step or 1))
        else:
            return islice(self._all(), ndx, ndx+1).next()





def check_param(*args, **kwargs):
    '''riceve una lista di nomi di parametri attesi 
    e una lista di parametri su cui effettuare il check
    >>> check_param({"attesi":("nome","cognome"),"nome":"stefano", "cognome":"borgia"})
    '''
    parametri_mancanti = ""
    for parametro in kwargs["attesi"]:
        if not kwargs.get(parametro):
            parametri_mancanti += parametro
            
    errore = "parametri mancanti ".parametri_mancanti
    return errore


def datetime_conversion(date_time):
    '''riceve una data e ora nel formato accettati e lo converte in un oggetto datetime.datetime
    formati:
    YYYY-MM-DD HH:MM[:SS]
    YYYYMMDD HH:MM[:SS]
    YYYYMMDD HHMMSS
    '''
    logger.debug("conversione data %s:" % date_time)
    #format_list = ["(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})", "(\d{4})(\d{2})(\d{2}) (\d{2}):(\d{2}):(\d{2})", \
    #                   "(\d{4})(\d{2})(\d{2}) (\d{2}):(\d{2})", "(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})",\
    #                   "(\d{4})(\d{2})(\d{2}) (\d{2})(\d{2})(\d{2})",]
    
    format_list = ['(\d{4})(\d{2})(\d{2}) (\d{2})(\d{2})(\d{2})', '(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})',]
    for format in format_list:
        m = re.match(format, date_time)
        if m:
            # TODO considerare il caso senza secondi
            #return datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)))    
            return datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)))
        
    logger.debug("la data %s ha un formato non accettato" %date_time)
    print "la data %s ha un formato non accettato" %date_time
    return None
        

def interrogate(item):
    """Print useful information about item."""
    if hasattr(item, '__name__'):
        print "NAME:    ", item.__name__
    if hasattr(item, '__class__'):
        print "CLASS:   ", item.__class__.__name__
    print "ID:      ", id(item)
    print "TYPE:    ", type(item)
    print "VALUE:   ", repr(item)
    print "CALLABLE:",
    if callable(item):
        print "Yes"
    else:
        print "No"
    if hasattr(item, '__doc__'):
        doc = getattr(item, '__doc__')
        doc = doc.strip()   # Remove leading/trailing whitespace.
        firstline = doc.split('\n')[0]
        print "DOC:     ", firstline

