"""
Script to filter targets from the TNS database, calaculate how long they're visible for on the night
in question and uses this information along with their transit altitude, lunar separation, time
discovered, time modified, and magnitude to calculate a priorty score for observing them with the
Liverpool Telescope on La Palma, España.

Depends on filter_funcs.py script to operate.

Author: George Hume
2022
"""

### IMPORTS ###
import csv
import numpy as np
import datetime as dt
from functions import *

# loads in the tns database as numpy array along with
#the date it was released as a string and a list of the headers
date, headers, database = loadDB("/home/pha17gh/TNS/tns_public_objects.csv")
Tday = dt.datetime.combine(dt.datetime.now(), dt.datetime.min.time()) #today's data at turn of the day
todaySTR = Tday.strftime('%Y-%m-%d %H:%M:%S')

DB = TNSlice(database,todaySTR) #new database with relevant transients from last 2 weeks

#extract the relevant columns from the database
IDs = DB.T[0]
prefix, name = DB.T[1], DB.T[2]
ra, dec = DB.T[3], DB.T[4]
t_disc, t_mod = DB.T[12],DB.T[-1]
mags = DB.T[13]

num = IDs.size

#location of Liverpool Telescope
lat = 28.6468866 #latitude in degs
long = -17.7742491 #longitude in degs
elv = 2326.0 #elevation in metres

#find the observable time, transit altitude, and lunar separation
t_obs, t_alt, l_sep = Visibility(todaySTR, ra, dec, lat, long, elv)

#from new database with columns for ID, name, ra, dec, t_disc t_mod, mag, t_obs, t_alt & lsep
num = IDs.size
newDB = np.array([IDs,prefix,name,ra,dec,t_disc,t_mod,mags,t_obs,t_alt,l_sep]).T
#needs to be transposed so can remove entries with 0 observable time

#remove targets with no observable time and find the priorty scores of the rest
PSweights = [10,5,1,0,0] #weighting for the different contribitions towards the pscore
finalDB = pscore(newDB,PSweights) #final database includeing the priorty scores in last column

#create a new list of headers for the new database (as have removed columns and added new ones)
newHeaders = flatten([headers[0:5], [headers[12], headers[-1],headers[13], "observable_time", "transit_alt", "lunar_sep", "priorty_score"]])

#dates to go before headers to give context
dates = [f"List calculated for {todaySTR} using TNS database from {date}"]

#save out the new database
filename = "/home/pha17gh/TNS/transient_list.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow(dates)
    csvwriter.writerow(newHeaders) #add headers first row
    csvwriter.writerows(finalDB) # write the rest of the data
