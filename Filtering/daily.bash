#!/bin/bash

yesterday=$(date -u --date="yesterday" +'%Y%m%d') #date yesterday in utc

#download the update
curl -X POST -H 'user-agent: tns_marker{"tns_id":142993,"type": "bot", "name":"BillyShears"}' -d 'api_key=b9d40748683e621a019ffd4e472fa862b2f20755' https://www.wis-tns.org/system/files/tns_public_objects/tns_public_objects_${yesterday}.csv.zip > /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv.zip

#unzip update and remove archive
unzip /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv.zip -d /home/pha17gh/TNS/
rm /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv.zip

#run python script to update data database
python /home/pha17gh/TNS/new_tns_update.py

#move updates to old updates file
mv /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv /home/pha17gh/TNS/old_updates/

#copy old pscores csv to directory
cp  /home/pha17gh/TNS/transient_list.csv /home/pha17gh/TNS/old_pscores/transient_list_${yesterday}.csv

#run filtering and pscore calculator
python /home/pha17gh/TNS/filter.py
