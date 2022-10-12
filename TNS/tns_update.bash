#!/bin/bash

yesterday=$(date -u --date="yesterday" +'%Y%m%d') #date yesterday in utc

#download the update
curl -X POST -H 'user-agent: tns_marker{"tns_id":142993,"type": "bot", "name":"BillyShears"}' -d 'api_key=b9d40748683e621a019ffd4e472fa862b2f20755' https://www.wis-tns.org/system/files/tns_public_objects/tns_public_objects_${yesterday}.csv.zip > tns_public_objects_${yesterday}.csv.zip

#unzip update and remove archive
unzip tns_public_objects_${yesterday}.csv.zip
rm tns_public_objects_${yesterday}.csv.zip

#run python script to update data database
python tns_update.py

#move updates to old updates file
mv tns_public_objects_${yesterday}.csv old_updates
