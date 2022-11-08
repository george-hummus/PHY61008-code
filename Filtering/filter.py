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
dateSTR, headers, database = loadDB("tns_public_objects.csv")

DB = TNSslice(database,date) #new database with relevant transients

#extract the relevant columns from the database
IDs = DB.T[0]
prefix, name = DB.T[1], DB.T[2]
ra, dec = DB.T[3], DB.T[4
t_disc, t_mod = DB.T[12],DB[-1]
mags = DB.T[13]

#location of Liverpool Telescope
lat = 28.6468866 #latitude in degs
long = -17.7742491 #longitude in degs
elv = 2326.0 #elevation in metres
