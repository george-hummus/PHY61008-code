#!/bin/bash

yesterday=$(date -u --date="yesterday" +'%Y%m%d') #date yesterday in utc

#download the update
curl -X POST -H 'user-agent: tns_marker{"tns_id":142993,"type": "bot", "name":"BillyShears"}' -d 'api_key=SECRET' https://www.wis-tns.org/system/files/tns_public_objects/tns_public_objects_${yesterday}.csv.zip > /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv.zip

#unzip update and remove archive
unzip /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv.zip -d /home/pha17gh/TNS/
rm /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv.zip

#run python script to update data database
python /home/pha17gh/TNS/tns_update.py

#move updates to old updates file
mv /home/pha17gh/TNS/tns_public_objects_${yesterday}.csv /home/pha17gh/TNS/old_updates/
