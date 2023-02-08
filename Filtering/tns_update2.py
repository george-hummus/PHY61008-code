"""
Script that updates the local TNS database with the updates downloaded via curl from the TNS.

Depends on filter_funcs.py script to operate.

Author: George Hume
2023
"""

import csv
import json
import numpy as np
import datetime as dt
import subprocess
from filter_funcs import *

DBname = "/home/pha17gh/TNS/tns_public_objects.csv" #database file name

#load in string of date, headers and database entries from the database
DBdate, headers, database = loadDB(DBname)

#datetime dates
DB_date = dt.datetime.strptime(DBdate, '%Y-%m-%d %H:%M:%S') #date from tns database
today = dt.datetime.combine(dt.datetime.now(), dt.datetime.min.time()) #today's data at turn of the day

#time difference between the dates
deltaT = (today - DB_date).days #time diff in days

if deltaT == 0:
	print("TNS database is already up to date")

elif deltaT == 1:
	#if only 1 day diff then download yesterday's updates and add to database
	udate = DB_date.strftime('%Y%m%d')
	DandU(udate,today,database,headers)

elif (deltaT>1) & (deltaT<=25):
	#if between 2 and 25days difference then download all previous updates and add then to database

	for i in range(deltaT):
    	#go from last to most current update

    	#date as string to find update file
		udate = DB_date.strftime('%Y%m%d')
    	next_day = DB_date+dt.timedelta(days=1)

    	#do the update for that date
    	DandU(udate,next_day,database,headers)

    	#load new database that was just saved so it can be overwritten again
    	DBdate, headers, database = loadDB(DBname)
		DB_date = dt.datetime.strptime(DBdate, '%Y-%m-%d %H:%M:%S') #convert next date into datetime object

else:
	#if over 25days difference then redownload the whole database from the TNS

	#string that constitutes the curl command for downloading
	cmd = '''curl -X POST -H 'user-agent: tns_marker{"tns_id":142993,"type": "bot", "name":"BillyShears"}' -d 'api_key=SECRET' https://www.wis-tns.org/system/files/tns_public_objects/tns_public_objects.csv.zip > /home/pha17gh/TNS/tns_public_objects.csv.zip'''

	#do the curl command to download the database
	subprocess.call(cmd,shell=True)

	#unzip the csv and delete the zip file
	uzip = "unzip /home/pha17gh/TNS/tns_public_objects.csv.zip -d /home/pha17gh/TNS/"
	rem = "rm /home/pha17gh/TNS/tns_public_objects.csv.zip"
	subprocess.call(uzip,shell=True)
	subprocess.call(rem,shell=True)
