#!/bin/bash

yesterday=$(date -u --date"yesterday" +"%Y%m%d")
sub_date=$(date +"%d/%m/%Y")
fname_date=$(date +"%Y%m%d")

rm /home/pi/mail/transient_list_${yesterday} #removes yesterdays list of transients

scp pha17gh@astrolab1.shef.ac.uk:/home/pha17gh/TNS/transient_list.csv /home/pi/mail/transient_list_${fname_date}.csv #downloads todays list of transients from astrolab

mail -s "Transients for ${sub_date}" ghume1@sheffield.ac.uk,j.maund@sheffield.ac.uk -A /home/pi/mail/transient_list_${fname_date}.csv < /home/pi/mail/transient-mail.txt #sends list to Justyn and I
