"""
Script to find the visibility of transients at a given position and date from their RA and Dec from the TNS alert CSV file.

Author: George Hume
2022
"""

### IMPORTS ###
import datetime as dt
from skyfield import almanac
from skyfield.api import N, E, wgs84, load, utc, Star
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import json
import csv
import argparse

### SYSTEM ARGUMENTS ###
parser = argparse.ArgumentParser(description = """
Given the RA and dec of a transient the script will calculate its visibility for a specified location and date. The visibility includes the range of altitudes of the target for the night of the given date  , the time it is visible in dark time,
""")

#adding arguments to praser object
parser.add_argument('date' , type = str, help = 'Date of the start of the night. In format "dd/mm/yyyy".')

parser.add_argument('lat' , type = float, help = 'Lattitude of the follow-up telescope.')
parser.add_argument('long' , type = float, help = 'Longitude of the follow-up telescope.')
parser.add_argument('elv' , type = float, help = 'Elevation above sea-level of the follow-up telescope.')

parser.add_argument('tns_alerts' , type = str, help = 'File name of CSV file containing the alerts.')

args = parser.parse_args()


#unpack the date
date = dt.datetime.strptime(args.date, "%d/%m/%Y")
date = date.replace(tzinfo=utc)

### Set-up ephemerides ##
#loads in ephemerides and time scle
eph = load('de421.bsp')
ts = load.timescale()
#sets up sun, earth (needed for calculating dark time and our location respectivly) and moon (for illumination)
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']
location = wgs84.latlon(args.lat * N, args.long * E, elevation_m = args.elv)
Epos = earth + location #sets up observing position (i.e., the postion of the follow-up telescope)

#ingest the CSV File
alerts=open(args.tns_alerts) #opens the csv file
csvreader = csv.reader(alerts) #opens file as csv
csv_date = next(csvreader) #first row which is the date the CSV file was created
headers = next(csvreader) #second row contains the headers of the CSV file
#now need to extract all the rows and save as numpy array
rows = []
for row in csvreader:
        rows.append(row)
rows = np.array(rows,dtype="object")

#turn the rows into dictonaries so they are easily indexable
tar_list = [] #list that will contain the dictonaries of each target
for i in range(rows.shape[0]): #loop over each entry
    target = rows[i]
    prop_dict = {} #dict to be filled with targets properties
    for j in range(rows.shape[1]): #loop over each element
        prop_dict[headers[j]] = target[j] #save each property using key from headers
    tar_list.append(prop_dict)

#need the local midday and the next day midday to calculate the dark time
t0 = ts.from_datetime(date)
t1 = t0 +  dt.timedelta(days=1) #calculate between date today and tomorrow

#this finds merdian transit of the sun (i.e., midday) in la palma (plus the anitmeridian transit)
f = almanac.meridian_transits(eph, sun, location)
t, y = almanac.find_discrete(t0, t1, f)

#merdian transit / midday
midday = t[list(y).index(1)]
midday2 = midday + dt.timedelta(days=1) #midday of next day

#find when it gets dark
f = almanac.dark_twilight_day(eph, location)
times, events = almanac.find_discrete(midday, midday2, f)

sunset = times[0]
darkstart = times[3]
darkend = times[4]
sunrise = times[7] #using the indcies to extract the different times of night
nightphases = [sunset,darkstart,darkend,sunrise] #savetogether as list for when calculating alts

all_dict = {} #dictonary to contain results form all targets

#find altitude of each transient at sunset, start of dark time, end of darktime, and sunrise
for k in tar_list:
    #RA and Dec of target in decimal degrees
    RA = float(k["ra"])
    dec = float(k["declination"])

    #convert to RA(h:m:s) & Dec(d:m:s)
    RAh = RA/15
    ra_hours = int(RAh)
    RAm = (RAh - ra_hours)*60
    ra_mins = int(RAm)
    ra_secs = (RAm - ra_mins)*60

    dec_degs = int(dec)
    DECm = (dec - dec_degs)*60
    dec_mins = int(DECm)
    dec_secs = (DECm - dec_mins)*60

    #cretes star object from RA and Dec which represents the transient
    transient =  Star(ra_hours=(ra_hours, ra_mins, ra_secs),
                       dec_degrees=(dec_degs, dec_mins, dec_secs))
    altitudes = []
    for l in nightphases:
        astro = Epos.at(l).observe(transient)
        app = astro.apparent()
        #observers star at time from position
        alt, az, distance = app.altaz()
        altitudes.append(alt.degrees)

    #making dictionary that contains the outputs
    Toutput = {"name":k['name_prefix']+k['name'],"RA":f"{ra_hours}:{ra_mins}:{round(ra_secs,6)}","Dec":f"{dec_degs}:{dec_mins}:{round(dec_secs,6)}","altitudes":{"sunset":round(altitudes[0],6),"darktime-start":round(altitudes[1],6),"darktime-end":round(altitudes[2],6),"sunrise":round(altitudes[3],6)}
    }

    all_dict[k["objid"]] = Toutput


#calculate moon's alt, phase, and illumination and middle of dark time
middledark = darkstart + (darkend-darkstart)
mastro = Epos.at(middledark).observe(moon)
mapp = mastro.apparent()
malt, maz, mdst = mapp.altaz()
mphase = almanac.moon_phase(eph, middledark)
mill = almanac.fraction_illuminated(eph,"moon",middledark)


output = {"location":{"latitude":args.lat,"longitude":args.long,"elevation":args.elv},
"date":args.date,
"night_phases":{"sunset":sunset.utc_strftime("%H:%M:%S %d/%m/%Y"),"darktime-start":darkstart.utc_strftime("%H:%M:%S %d/%m/%Y"),"darktime-end":darkend.utc_strftime("%H:%M:%S %d/%m/%Y"),"sunrise":sunrise.utc_strftime("%H:%M:%S %d/%m/%Y")},
"moon":{"alt": round(malt.degrees,6), "phase-degs": round(mphase.degrees,6), "illumination-percent": round(mill,6)},
"targets":all_dict
}

#save output dict as json
with open('transients.json', 'w') as fp:
        json.dump(output, fp,indent=4)
