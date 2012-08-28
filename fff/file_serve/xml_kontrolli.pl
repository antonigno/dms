#!/usr/bin/perl -w
#
# v0.2 - author Klemend Luari
# Improved version of xml_kontrolli.pl
#
# Da distribuire con tutte le librerie contenute nella ${ ese_pd }/scripts/lib
#

BEGIN {

	use Cwd 'abs_path';
        $WORKDIR  = abs_path($0) ;
        $WORKDIR  =~ s/(.*)\/\S+/$1/  ; 
	my $lib = $WORKDIR . '/lib';
	push( @INC, $lib );

}

use Reduction;
use Date;
use Getopt::Std;
use Time::Local;
use HTML::Entities;
use Fcntl qw(:flock);
use Sys::Hostname;
use vars qw( %conf $date %option $WORKDIR $hour $ora $primo @xml @ora $secondo $controllo );

getopts("s", \%option);

$date = Date->new();
my $today = $date->calculate();
( $hour = Date->time() ) =~ s/(\d{2})\:\d{2}\:\d{2}/$1/;
($data = Date->time()) =~ s/(\d{2})\:(\d{2})\:(\d{2})/$1$2$3/  ;  
my $hostname = hostname();
my $header=0;
my $applicativa = getpwuid( $< );
my $CONF=('controlli_'.$hostname.'_'.$applicativa);
my $CHIAVE="legnux_key";
#my $FILE='tmp_' . $hostname .  '.xml';
#my $FILE='tmp_' . $hostname.'_xml_'.$applicativa. '.tmp';
my $FILE= $hostname.'_xml_'.$applicativa.'_'.$today.$data.'.tmp';
my $LOCK = '/tmp/xml_kontrolli_' . $hostname.'_'.$applicativa. '.lock';
my $SERVER1 = '10.41.9.26';
my $DESTDIR1 = '/srv/esercizio/trunk/backend/RCV';
$scp_path = qx{ which scp };
chomp( $scp_path );

# Highlander
open(Self , ">",$LOCK ) or die "Cannot open $0 - $!";
unless( flock(Self , LOCK_EX|LOCK_NB ) ) {
print "There can be only one! $0 is already running, exiting.\n";
    exit( 1 );
}

sub xml{
  my @pars = @_;
  my @ora = split(/-/, $pars[2]);
  if ($ora[0] == $ora[1] || ($hour>=$ora[0] && $hour<=$ora[1])){
    $today =~ /(\d{4})(\d{2})(\d{2})/; #Modifico la data in base agli standard richiesti dal db
    my $oggi = $1."-".$2."-".$3;
    my @out = `$_[0]`; #Lancio lo script e salvo l'output relativo
    foreach (@out){
      encode_entities($_);
    }
    my $errori = 0;
    my $link = 0;
    my ( @err, @output, @links );
    foreach (@out) {
      if (m/ERRORI_CONTROLLO:/){
        $errori = 1;
        next;
      }
      if (m/INFO_LINK:/){
        $link = 1;
         next;
      }
      if ($link){
	push (@links, $_);
      }
      elsif ($errori){
        push (@err, $_);
      }else{
        push (@output, $_);
      }
    }

    @output = Reduction->transform(\@output);
    if (@err){
      @err = Reduction->transform(\@err);
    }

    $ora = $date->time();
    $primo = "<controllo><nome_macchina>$hostname</nome_macchina><nome>$pars[1]</nome><script>$pars[0]</script><versione>$pars[3]</versione><data>$oggi</data><ora>$ora</ora><esito></esito><errori>";
    $secondo = "</output></controllo>";
    push (@xml, $primo, @err, "</errori>");
    if ($link) {
			  push(@xml, "<link>", @links, "</link>"); 
    }
    push(@xml, "<output>", @output, $secondo);
  }
}


open(CONT,"<", "$WORKDIR/$CONF") or die "Can't open $WORKDIR/$CONF"; #Apre il file di configurazione
my @cont=<CONT>;
foreach $controllo (@cont){ #Per ogni riga
  if($controllo !~ /^\s*#/ && $controllo !~ /^\s*$/){ #Se non e' un commento o una riga vuota
    my @pars = split(/\s{2,}/, $controllo); #Divide i campi dove ci sono 2 o piu' spazi
    chomp(@pars);
    if (defined $option{s}){  #Se lo script viene lanciato con l'opzione -s (lanciato da crontab)
      if ($header == 0){
        @xml = "<ccc xmlns=\"http://www.ced-padova-opsc.com\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">";
        $header=1;
      }

      xml(@pars); #Funzione di generazione xml

    }else{
      @ora = split(/-/, $pars[2]); #Nell'array ora inserisce l'ora di inizio e fine validita'
      if ($ora[0] == $ora[1] || ($hour>=$ora[0] && $hour<=$ora[1])){ #Se siamo all'interno di questo orario o se i due orari coincidono esegui lo script
        system("clear");
        print "\n$pars[1]\n\n"; #Visualizza il nome evidenziato
        system("$pars[0]"); #Esegue lo script
        print "\n\nPremere invio per continuare\n";
        <STDIN>; #Aspetta un input per procedere
        system("/usr/bin/clear"); 
      }
    }
  }
}
close(CONT);

if ( $header == 1 ) {

 push (@xml,"</ccc>");
 open(TMP,">$WORKDIR/$FILE");
 print TMP @xml;
 close TMP;
 #qx{ $scp_path  -i ${WORKDIR}/${CHIAVE} ${WORKDIR}/${FILE} god\@${ SERVER1 }:${ DESTDIR1 }/${ hostname }_xml_${ today }\.tmp };
 qx{ $scp_path  -i ${WORKDIR}/${CHIAVE} ${WORKDIR}/${FILE} god\@${ SERVER1 }:${ DESTDIR1 }/${ FILE } };
}

unlink("$WORKDIR/$FILE") or die "$!";


