#!/bin/bash
echo "" #gap between log entries
date -u #prints the date out for the log

#run python script to download updates and update the database
python /home/pha17gh/TNS/tns_update2.py

#move all updates to old updates directory
mv /home/pha17gh/TNS/tns_public_objects_* /home/pha17gh/TNS/old_updates/

#copy old pscores csv to directory
cp  /home/pha17gh/TNS/transient_list.csv /home/pha17gh/TNS/old_pscores/transient_list_${yesterday}.csv

#run filtering and pscore calculator
python /home/pha17gh/TNS/filter.py
