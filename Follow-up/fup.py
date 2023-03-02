"""
Follow-up script that sends targets from the priorty score lists to be observed with the LT.

Author: George Hume
2023
"""

### IMPORTS ###

import ltrtml
import csv
import numpy as np
import datetime as dt
from fup_funcs import *
import json


### Set up targets ###

# load in the PEPPER Fast priority list CSV file
info, headers, flist = loadDB("transient_list-F.csv")

nrows = flist.shape[0] #number of entries in list

#extract top targets
if nrows > 5: #if over 5 pick the top 5
    top = flist[0:5]
elif nrows != 0: #if less than 5 and greater than 0 then pick all
    top = flist[0:]
else: #if no rows (blank list) then quit (dont request any observations)
    print("No sutible targets to request observations of.")
    exit()

#create list of dicts containing the transients names and RA and Dec in correct format for ltrtml
targets = tar_dicts(top)


### Set up constraints ###
# we want to request the observations as soon as we get the list so constraints in time will be from when released to start of morning twilight on the next day (over 24hrs away if release at 01:10 local time)

# start date and time
now = dt.datetime.utcnow()
sdate = now.strftime("%Y-%m-%d")
stime = now.strftime("%H:%M:%S")

# end date and time
# open file containing the times sunset/rise and twilight times for the night ahead
with open('solar_times.json') as json_file:
    sdict = json.load(json_file)
edate = sdict["nightend_date"]
etime = sdict["darkend"] #end on morning twilight of the next day

# make the constraints dict
constraints = {
    'air_mass': '1.74',           # 1.7 airmass corresponds to 35deg alt
    'sky_bright': '1.0',          # We dont need a max as are targets shouldn't be near the moon
    'seeing': '1.2',              # Maximum allowable FWHM seeing in arcsec (ask J)
    'photometric': 'yes',         # Photometric conditions, ['yes', 'no'] (ask J - probs yes)
    'start_date': sdate,          # Start Date should be today
    'start_time': stime,          # Start Time should be when darktime starts
    'end_date': edate,            # End Date should be next day
    'end_time': etime,            # End Time when
}


### Set up observations ###
# we want to observe with MOPTOP in the R-band for 880s with slow rot speed for all targets

# make a list of observation dicts for each target
obs = []

for target in targets:
    observation = {
        'instrument': 'Moptop',
        'target': target,
        'filters': {'R': {'exp_time': '880',    # Exposure time is 880 seconds
                          'rot_speed': 'slow'}}}  # Rotor speed is slow
    obs.append(observation)


### Set up the credentials ###
# need to load the settings in from separate json - these are secrete so don't publish

with open('creds.json') as json_file:
    settings = json.load(json_file)


### Set up connection to the LT ###
try:
    obs_object = ltrtml.LTObs(settings)
except:
    print("could not access the LT - please check credentials")

### Send Observation request and save group ids ###
#uid, error = obs_object.submit_group(obs, settings) #real
uid, error = np.random.randint(234321,367990, size=top.shape[0]), "blah blah blah" #test

#make dictonary with uids as keys and target info as content and save as json
obs_dict = {}
for i, target in enumerate(targets):
    obs_dict[str(uid[i])] = target

#save any errors to the json also
obs_dict["errors"] = error
try:
    with open(f"observations.json","+") as fp: #read and write
        allobs = json.load(json_file)
        allobs[sdate] = obs_dict
        json.dump(allobs, fp, indent=4)
except:
    allobs = {}
    allobs[sdate] = obs_dict
    with open(f"observations.json","w") as fp: #read and write
        json.dump(allobs, fp, indent=4)
