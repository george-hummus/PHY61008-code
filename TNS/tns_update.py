"""
Script that updates the local TNS database with the updates downloaded via curl

Author: George Hume
2022
"""

import csv
import json
import numpy as np
import datetime as dt

#dates used to load in files and add to top of csv
today = dt.datetime.utcnow() 
yesterday = today - dt.timedelta(days=1)

#load in the fulldata base
file=open("tns_public_objects.csv") #load in database
csvreader = csv.reader(file) #openfile as csv
next(csvreader) #skip the date
headers = next(csvreader) #save headers
database = []
for row in csvreader:
        database.append(row) #save all rows into a list
#convert list into numpy array
database = np.array(database,dtype="object")

#now load in the CSV with the updates
file2=open(f"tns_public_objects_{yesterday.strftime('%Y%m%d')}.csv") #load in updates from previous day
csvreader2 = csv.reader(file2) #openfile as csv
next(csvreader2) #skip the date
next(csvreader2) # skip the header
updates = []
for row in csvreader2:
        updates.append(row) #save all rows into a list
#convert list into numpy array
updates = np.array(updates,dtype="object")

#now need to loop through each entry in the updates  and find match/ or add if new to the database
#need to loop from bottom to top so to add newest entries to the top of the database
for i in range(len(updates)):
    row = updates[-(i+1)] #extarcts rows from bottom upwards (index -1 -> -len)
    ID = row[0] #get the id of the update
    IDrow = np.where(database == ID)[0] # looks for row corresponding to ID in the database

    if IDrow.size == 0: #if id is not in database then this is a new ID
        database = np.vstack([row,database]) #inserts new ID at the top of the database
    else: #if it is in database then we need to update the entry
        database[IDrow][0] = row

database = np.vstack([headers,database]) #add the headers back to the top

#save out the database
filename = "tns_public_objects.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow([today.strftime('%d-%m-%Y')]) #add date to first row
    csvwriter.writerows(database) # write the headers and rest of the data
