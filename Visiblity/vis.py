"""
Script to find the visibility of transients at a given position and date from their RA and Dec.

Author: George Hume
2022
"""

import datetime as dt
from skyfield import almanac
from skyfield.api import N, E, wgs84, load, utc, Star
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser(description = """
Given the RA and dec of a transient the script will calculate its visibility for a specified location and date. The visibility includes the range of altitudes of the target for the night of the given date  , the time it is visible in dark time,
""")

#adding arguments to praser object
parser.add_argument('date' , type = str, help = 'Date of the start of the night. In format "dd/mm/yyyy".')

parser.add_argument('lat' , type = float, help = 'Lattitude of the follow-up telescope.')
parser.add_argument('long' , type = float, help = 'Longitude of the follow-up telescope.')
parser.add_argument('elv' , type = float, help = 'Elevation above sea-level of the follow-up telescope.')

parser.add_argument('ra_hours' , type = int, help = 'Hours of RA of transient.')
parser.add_argument('ra_mins' , type = int, help = 'Mintues of RA of transient.')
parser.add_argument('ra_secs' , type = float, help = 'Seconds of RA of transient.')

parser.add_argument('dec_degs' , type = int, help = 'Degrees of declination of transient.')
parser.add_argument('dec_mins' , type = int, help = 'Arcmintues of declination of transient.')
parser.add_argument('dec_secs' , type = float, help = 'Arcseconds of declination of transient.')

args = parser.parse_args()

#unpack the date
date = dt.datetime.strptime(args.date, "%d/%m/%Y")
date = date.replace(tzinfo=utc)

### Set-up ephemerides ##
#loads in ephemerides and time scle
eph = load('de421.bsp')
ts = load.timescale()
#sets up sun and earth - needed for calculating dark time and our location respectivly
earth, sun = eph['earth'], eph['sun']
location = wgs84.latlon(args.lat * N, args.long * E, elevation_m = args.elv)
Epos = earth + location #sets up observing position (i.e., the postion of the follow-up telescope)

#cretes star object from RA and Dec which represents the transient
transient =  Star(ra_hours=(args.ra_hours, args.ra_mins, args.ra_secs),
                   dec_degrees=(args.dec_degs, args.dec_mins, args.dec_secs))

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

#find altitude of transient at sunset, start of dark time, end of darktime, and sunrise
altitudes = []
for i in nightphases:
    astro = Epos.at(i).observe(transient)
    app = astro.apparent()
    #observers star at time from position
    alt, az, distance = app.altaz()
    altitudes.append(alt.degrees)

#making dictonary that contains the outputs
output = {"location":{"lattitude":args.lat,"longitude":args.long,"elevation":args.elv},
"date":args.date,
"night_phases":{"sunset":sunset.utc_strftime("%H:%M:%S %d/%m/%Y"),"darktime-start":darkstart.utc_strftime("%H:%M:%S %d/%m/%Y"),"darktime-end":darkend.utc_strftime("%H:%M:%S %d/%m/%Y"),"sunrise":sunrise.utc_strftime("%H:%M:%S %d/%m/%Y")},
"target":{"name":"transient1","RA":f"{args.ra_hours}:{args.ra_mins}:{args.ra_secs}","Dec":f"{args.dec_degs}:{args.dec_mins}:{args.dec_secs}",
"altitudes":{"sunset":altitudes[0],"darktime-start":altitudes[1],"darktime-end":altitudes[2],"sunrise":altitudes[3]}}
}

#save output dict as json
with open(f'transient1.json', 'w') as fp:
        json.dump(output, fp,indent=4)
