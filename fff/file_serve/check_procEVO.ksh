#!/usr/bin/ksh
# Controllo presenza processi applicativi
# Matteo Basso UE022701
# Egidio Menini
# ver. 1   12/10/2009
# ver. 2   15/10/2010
# ver. 2.1 20/10/2010
# ver. 2.2 23/10/2010
# ver. 2.3 28/10/2010
# in fase di modifica

HOSTNAME=`hostname`
ERRORI=""
COUNTER=0

CheckNodeManager()
{
   START=startNodeManager
   echo "\033[1m$START\033[0m"
   VER=`ps -ef | grep $START | grep -v grep`
   ps -ef |grep java1.5 | grep client | grep -v grep | wc -l | bc | read COUNT_START
   if [ -n "$VER" ]
   then
      echo "PADRE:`print $VER | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      echo "FIGLIO:`ps -ef | grep java1.5 | grep client | grep -v ThreadPoolSize | grep -v grep | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   elif [ $COUNT_START -ge 1 ]
   then
      echo "Non e' presente il processo startNodeManager ma il suo figlio, TUTTO OK!"
      echo "FIGLIO:`ps -ef | grep java1.5 | grep client | grep -v ThreadPoolSize | grep -v grep | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   else
      echo "\033[0;5mATTENZIONE, NON sono presenti ne padre ne figlio!!! Processo DOWN\033[0m"
      ERRORI=$ERRORI" "$START
   fi
}

Check_WLS()
{
   PROC=$1
   echo "\033[1m$PROC\033[0m"
   VER=`ps -ef | grep $PROC | grep -v grep`
   if [ -n "$VER" ]
   then
      echo "NIPOTE:`print $VER | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   else
      echo "\033[0;5mATTENZIONE, processo non presente!!!\033[0m"
      ERRORI=$ERRORI" "$PROC
   fi
}

# Controllo per il solo processo startNodeManager, se manca verifica i figli
Check_startWebLogic()
{
   LOG=WebLogic.sh
   echo "\033[1m$LOG\033[0m"
   VER=`ps -ef | grep $LOG | grep -v grep`
   ps -ef |grep java1.5 | grep server | grep -v grep | wc -l | bc | read COUNT_LOG
   if [ -n "$VER" ]
   then
      echo "NONNO:`print $VER | awk '{print $11\" \"$12\" \"$13\" ---> \"$19\" \"$20}'`"
      echo "PADRE:`print $VER | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      echo "FIGLIO:`ps -ef | grep java1.5 | grep server | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   elif [ $COUNT_LOG -ge 1 ]
   then
      echo "Non e' presente il processo log_engine_server ma il suo figlio, TUTTO OK!"
      echo "FIGLIO:`ps -ef | grep java1.5 | grep server | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   else
      echo "\033[0;5mATTENZIONE, NON sono presenti ne padre ne figlio!!! Processo DOWN\033[0m"
      ERRORI=$ERRORI" "$START
   fi     
}

Check_start()
{
   LOG=start.sh
   echo "\033[1m$LOG\033[0m"
   VER=`ps -ef | grep $LOG | grep -v grep`
   ps -ef | grep java1.5 | grep rmFileLoader | grep -v grep | wc -l | bc | read COUNT_LOG
   if [ -n "$VER" ]
   then
      echo "PADRE:`print $VER | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      echo "FIGLIO:`ps -ef | grep java1.5| grep rmFileLoader | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   elif [ $COUNT_LOG -ge 1 ]
   then
      echo "Non e' presente il processo start.sh ma il suo figlio,TUTTO OK!"
      echo "FIGLIO:`ps -ef | grep java1.5 | grep rmFileLoader | awk '{print $1\" \"$2\" \"$3\" ---> \"$9\" \"$10}'`"
      COUNTER=`expr $COUNTER + 1`
   else
      echo "\033[0;5mATTENZIONE, NON sono presenti ne padre ne figlio!!! Processo DOWN\033[0m"
      ERRORI=$ERRORI" "$LOG
   fi
}

# Verifica se ci sono tutti i processi 
Count()
{
   if [ $COUNTER -ne $1 ]
   then
      echo "Sono presenti $COUNTER e ne devono essere presenti $1 ---> Controllo `tput smso` NOT OK `tput rmso`"
      echo "`tput smso` ATTENZIONE: mancano i seguenti processi applicativi: $ERRORI `tput rmso`"
      PRINT_ERR="ATTENZIONE: mancano i seguenti processi Applicativi: $ERRORI"
   else
      echo "Sono presenti $COUNTER e ne devono essere presenti $1 ---> Controllo `tput smso` OK `tput rmso`"
   fi
}

ROW()
{
   echo "-------------------------------------------------------------------------------"
}

# MAIN

echo "\033[1mProcessi Applicativi\033[0m\n"

case "$HOSTNAME" in
 "mvasbe1") CheckNodeManager; Check_WLS mvne_beao01;       Check_WLS mvne_bebss01; ROW; Count 3;;
 "mvasbe2") CheckNodeManager; Check_WLS mvne_beao02;       Check_WLS mvne_bebss02; ROW; Count 3;;
 "mvasfe1") CheckNodeManager; Check_WLS mvne_fese01;       Check_startWebLogic;    ROW; Count 3;;
 "mvasfe2") CheckNodeManager; Check_WLS mvne_fese02;  ROW; Count 2;;
 "mvasdb1") CheckNodeManager; Check_WLS mwvas01;           Check_WLS mwserv01;     ROW; Check_log_engine_server; ROW; Count 4;;
 "mvasdb2") CheckNodeManager; Check_WLS mwvas02;           Check_WLS mwserv02;     ROW; Count 3;;
 "mwnp1")   CheckNodeManager; Check_WLS rm_wb01;      ROW; Check_startWebLogic;    ROW; Check_start; ROW; Count 4;;
 "mwnp2")   CheckNodeManager; Check_WLS rm_wb02;      ROW; Check_startWebLogic;    ROW; Count 3;;
esac

echo "-------------------"
echo "ERRORI_CONTROLLO:"
echo $PRINT_ERR
