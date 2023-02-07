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
print("imported database")

DB = TNSlice(database,date) #new database with relevant transients
print("sliced database")

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
print("finding observable time")
t_obs, t_alt, l_sep = Visibility(date, ra, dec, lat, long, elv)
print("observable time found")

#from new database with columns for ID, name, ra, dec, t_disc t_mod, mag, t_obs, t_alt & lsep
num = IDs.size
newDB = np.concatenate(
[np.resize(IDs,[num,1]),
np.resize(prefix,[num,1]),
np.resize(name,[num,1]),
np.resize(ra,[num,1]),
np.resize(dec,[num,1]),
np.resize(t_disc,[num,1]),
np.resize(t_mod,[num,1]),
np.resize(mags,[num,1]),
np.resize(t_obs,[num,1]),
np.resize(t_alt,[num,1]),
np.resize(l_sep,[num,1])],axis=1)
print("made new database")

print("finding pscore")
#remove targets with no observable time and find the priorty scores of the rest
PSweights = [10,5,1] #weighting for the different contribitions towards the pscore
finalDB = pscore(newDB,PSweights) #final database includeing the priorty scores in last column
print("found pscores")

#create a new list of headers for the new database (as have removed columns and added new ones)
newHeaders = flatten([headers[0:5], [headers[12], headers[-1],headers[13], "observable_time", "transit_alt", "lunar_sep", "priorty_score"]])

#save out the new database
filename = "transient_list.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow(newHeaders) #add headers first row
    csvwriter.writerows(finalDB) # write the rest of the data

print("saved new list - finished")
