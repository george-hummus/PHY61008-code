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
from filter_funcs import *

# loads in the tns database as numpy array along with
#the date it was released as a string and a list of the headers
date, headers, database = loadDB("tns_public_objects.csv")

DB = TNSlice(database,date) #new database with relevant transients

#extract the relevant columns from the database
IDs = DB.T[0]
prefix, name = DB.T[1], DB.T[2]
ra, dec = DB.T[3], DB.T[4]
t_disc, t_mod = DB.T[12],DB[-1]
mags = DB.T[13]

#location of Liverpool Telescope
lat = 28.6468866 #latitude in degs
long = -17.7742491 #longitude in degs
elv = 2326.0 #elevation in metres

#find the observable time, transit altitude, and lunar separation
t_obs, t_alt, l_sep = Visibility(date, ra, dec, lat, long, elv)

#from new database with columns for ID, name, ra, dec, t_disc t_mod, mag, t_obs, t_alt & lsep
num = IDs.size
newDB = np.hstack([IDs.resize[num,1],prefix.resize[num,1],name.resize[num,1],
ra.resize[num,1],dec.resize[num,1],t_disc.resize[num,1],t_mod.resize[num,1],
mags.resize[num,1],t_obs.resize[num,1],t_alt.resize[num,1],l_sep.resize[num,1]])

#remove targets with no observable time and find the priorty scores of the rest
PSweights = [10,5,1] #weighting for the different contribitions towards the pscore
finalDB = pscore(newDB,PSweights) #final database includeing the priorty scores in last column

#create a new list of headers for the new database (as have removed columns and added new ones)
newHeaders = flatten([headers[0:5], headers[12], headers[-1],headers[13], "observable_time", "transit_alt", "lunar_sep", "priorty_score"])

#save out the new database
filename = "transient_list.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow(newHeaders) #add headers first row
    csvwriter.writerows(finalDB) # write the headers and rest of the data
