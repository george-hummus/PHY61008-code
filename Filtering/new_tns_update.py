"""
Script that updates the local TNS database with the updates downloaded via curl

Author: George Hume
2022
"""

import csv
import json
import numpy as np
import datetime as dt
from filter_funcs import *

DBname = "/home/pha17gh/TNS/tns_public_objects.csv" #database file name

#load in string of yesterday's date, headers and database entries
yesterdaySTR, headers, database = loadDB(DBname)

#dates used to load in update file and add to top of new csv
yesterday = dt.datetime.strptime(yesterdaySTR, '%Y-%m-%d %H:%M:%S')
today = yesterday + dt.timedelta(days=1)

#load in update entries (skip date and headers tho)
UDname = f"/home/pha17gh/TNS/tns_public_objects_{yesterday.strftime('%Y%m%d')}.csv" #updates filename
dummy1,dummy2,updates = loadDB(UDname)

#now need to loop through each entry in the updates  and find match/ or add if new to the database
#need to loop from bottom to top so to add newest entries to the top of the database
for i in range(len(updates)):
    row = updates[-(i+1)] #extarcts rows from bottom upwards (index -1 -> -len)
    ID = row[0] #get the id of the update
    IDrow = np.where(database == ID)[0] # looks for row corresponding to ID in the database

    if IDrow.size == 0: #if id is not in database then this is a new ID
        database = np.vstack([row,database]) #inserts new ID at the top of the database
    else: #if it is in database then we need to update the entry
        database[IDrow[0]] = row

database = np.vstack([headers,database]) #add the headers back to the top

#save out the database
filename = "/home/pha17gh/TNS/tns_public_objects.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow([today.strftime('%Y-%m-%d %H:%M:%S')]) #add date to first row
    csvwriter.writerows(database) # write the headers and rest of the data
