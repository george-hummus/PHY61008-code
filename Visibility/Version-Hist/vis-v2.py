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
from tqdm import tqdm

### SYSTEM ARGUMENTS ###
parser = argparse.ArgumentParser(description = """
Given the RA and dec of a transient the script will calculate its visibility for a specified location and date. The visibility includes the range of altitudes of the target for the night of the given date  , the time it is visible in dark time,
""")

#adding arguments to praser object
parser.add_argument('lat' , type = float, help = 'Lattitude of the follow-up telescope.')
parser.add_argument('long' , type = float, help = 'Longitude of the follow-up telescope.')
parser.add_argument('elv' , type = float, help = 'Elevation above sea-level of the follow-up telescope.')
parser.add_argument('tns_alerts' , type = str, help = 'File name of CSV file containing the alert updates. Needs form "tns_public_objects_YYYMMDD.csv"')
args = parser.parse_args()

# DATES #
filedate = args.tns_alerts[-12:-4] #date from end of the csv update
# get the date intrested in (day after date of csv) and the next day at 12pm and add UTC time zone
today = dt.datetime.strptime(filedate, '%Y%m%d') + dt.timedelta(days=1.5)
today =today.replace(tzinfo=utc)
tomorrow = today + dt.timedelta(days=1)
tomorrow = tomorrow.replace(tzinfo=utc)


### Set-up sky-field observing ##
location = wgs84.latlon(args.lat * N, args.long * E, elevation_m = args.elv) #location of observatory
ts = load.timescale() #loads in timescale
eph = load('de421.bsp')  #loads in ephemerides
#sets up sun, earth (needed for calculating dark time and our location respectivly) and moon (for illumination, etc.)
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']
Epos = earth + location #sets up observing position (i.e., the postion of the follow-up telescope)

#makes time objects from today and tomorrow
t0 = ts.from_datetime(today)
t1 = ts.from_datetime(tomorrow)


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


### Find the dark time start and end ###
f = almanac.dark_twilight_day(eph, location)
times, events = almanac.find_discrete(t0, t1, f)

sunset = times[0]
darkstart = times[3]
darkend = times[4]
sunrise = times[7] #using the indcies to extract the different times of night
nightphases = [sunset,darkstart,darkend,sunrise] #savetogether as list for when calculating alts

## calculate moon's alt, phase, and illumination ##
midnight = t0 + dt.timedelta(hours=12)
mastro = Epos.at(midnight).observe(moon)
mapp = mastro.apparent()
malt, maz, mdst = mapp.altaz()
mphase = almanac.moon_phase(eph, t0)
mill = almanac.fraction_illuminated(eph,"moon",midnight)
malt, mphase = malt.degrees, mphase.degrees


all_dict = {} #dictonary to contain results form all targets

## FUNCTIONS FOR CALCULATING OBSERVABLE TIME OF TARGET ##
def transit_time(tar,t_start,t_end):
    """
    Function that finds the transit time (in UTC) of a target between two times (need to be 24hrs apart)
    and the altitude of this transit in degrees.
    Arguments:
        - tar: the target as a skyfield Star object.
        - t0: start time as a skyfield time object.
        - t1: end time (should be ~24hrs later) as a skyfield time object.
    Output:
        t_time: time that the object transits in UTC as a skyfield time object.
        t_alt: altitude in degrees that the object transits (float).
    """
    #function that calculates transit
    f = almanac.meridian_transits(eph, tar, location)
    t, y = almanac.find_discrete(t_start, t_end, f)
    #t is times of transit,
    #y is array with 0 for antimerdian transit and 1 for meridian transit (which we are intrested in)

    #so t_time is the element at the same index as 1 in y in the t array
    meridian_index = np.where(y==1)[0]
    t_time = t[meridian_index]

    #now need to find altitude of star at this time
    astro = Epos.at(t_time).observe(tar)
    app = astro.apparent()
    alt, az, distance = app.altaz()
    t_alt = alt.degrees

    return t_time[0], t_alt[0]

def alt2HA(alt,lt,dec):
    '''
    Function that calculates the absolute value of the hour angle of a target for at a specified altitude,
    given the latitude of the location and the declination of the target.
    Arguments:
        - alt: the altitude you want to find the value of the HA at, in decimal degrees (float).
        - lt: the latitude of the location you are observing the target, in decimal degrees (float).
        - dec: the declination of the target, in decimal degrees (float)
    Output:
        - HA: the absolute value of the HA of the target at the specified altitude in decimal hours (float).
    '''

    #convert dec, lat and alt into radian
    altR = np.radians(alt)
    latR = np.radians(lt)
    decR = np.radians(dec)

    #find the hour angle of the
    cosHAnum = np.sin(altR) - (np.sin(latR)*np.sin(decR)) #numerator of cos(HA)
    cosHAden = np.cos(latR)*np.cos(decR) #denominator of cos(HA)
    cosHA = cosHAnum/cosHAden

    #find the hour angle using arccos
    HAdeg = np.degrees(np.arccos(cosHA)) #hour angle in degrees
    HA = HAdeg/15 #hour angle in hours

    return HA

def obs_time(dt_start,dt_end,rise_t,set_t):
    """
    Function that calculates how long a target is visible given the times dark time starts and ends, and
    the times the target rises above and sets below a certain altitude. Note all times need to be in
    the same timezone, idealy UTC.
    Arguments:
        - dt_start: the time dark time starts as a skyfield time object.
        - dt_end: the time dark time ends as a skyfield time object.
        - rise_t: the time the target rises above the certain altitude.
        - set_t: the time the target sets below the certain altitude.
    Output:
        t_obs: the time the target is obserable in dark time, as a decimal hour (float).
    """

    #convert the times into datetime objects
    dt_start, dt_end = dt_start.utc_datetime(), dt_end.utc_datetime()
    rise_t, set_t = rise_t.utc_datetime(), set_t.utc_datetime()

    ## Now need to carry out the flow chart described above ##
    #first check is rise_t greater than dt_start
    if rise_t > dt_start:
        #if true then target rises after dark time starts
        #next check: is rise_t greater than dt_end
        if rise_t > dt_end:
            #if true target rises and sets after dark time, so cant observe
            t_obs = 0
        else:
            #if false the target rises in dark time
            #next check: is set_t greater than dt_end
            if set_t > dt_end:
                #if true then target rises in dark time and then sets after
                #so observable time is end of dark time minus rise time
                t_obs = (dt_end - rise_t).seconds/3600 #have to divide by 3600 to get in hours
            else:
                #if false then target rises and sets in dark time
                #so observable time is just the time it is above the certain altitude
                t_obs = (set_t - rise_t).seconds/3600
    else:
        #if false target rises before dark time
        #next check: is set_t greater than dt_start
        if set_t > dt_start:
            #if true then the target sets in dark time
            #next check: is set_t greater than dt_end
            if set_t > dt_end:
                #if true then target rises before dark time and sets after it
                #so observable time is the length of dark time
                t_obs = (dt_end - dt_start).seconds/3600
            else:
                #if false then target rises before dark time and sets in dark time
                #so observable time is the set time minus the start of dark time
                t_obs = (set_t - dt_start).seconds/3600
        else:
            #if false then target rises and sets before dark time starts, so cant observe
            t_obs = 0

    return t_obs

#find altitude of each transient at sunset, start of dark time, end of darktime, and sunrise
for k in tqdm(tar_list):
    #RA and Dec of target in decimal degrees
    RA = float(k["ra"])
    Dec = float(k["declination"])

    #convert RA in decimal degrees to RA in hrs, mins, secs
    raH = RA/15 #RA decimal degrees to decimal hours
    ra_hours = int(raH) #hours of RA
    raM = (raH-ra_hours)*60 #decimal mintues of RA
    ra_mins = int(raM) #mintues of RA
    ra_secs = (raM-ra_mins)*60 #seconds of RA

    #convert DEC in decimal degrees to dec in degs, arcmins, arcsecs
    dec_degs = int(Dec) #degs of dec
    decM = (Dec-dec_degs)*60 #decimal arcmintues of dec
    dec_mins = int(decM) #arcmintues of dec
    dec_secs = (decM-dec_mins)*60 #arcseconds of dec

    #cretes star object from RA and Dec which represents the transient
    target =  Star(ra_hours=(ra_hours, ra_mins, ra_secs),dec_degrees=(dec_degs, dec_mins, dec_secs))

    #finding the UTC time the target transits the meridian
    trans_time, trans_alt = transit_time(target,t0,t1)

    # if the transit altitude is less than 35 then cant observe it #
    if trans_alt < 35:
        t_obs = 0
    else: #otherwise can continue

        # find the HA of target at 35 degs
        HA = alt2HA(35,args.lat,Dec)
        ## Find the time target rises above 35 and then sets below 35 using the HA and transit time ##
        rise35 = trans_time - dt.timedelta(hours=HA)
        set35 = trans_time + dt.timedelta(hours=HA)
        above35 = ((set35.utc_datetime()-rise35.utc_datetime()).seconds)/3600 #time above 35 degs

        #find the observable time f the target
        t_obs = obs_time(darkstart,darkend,rise35,set35)

    #making dictionary that contains the outputs
    Toutput = {
    "name":k['name_prefix']+k['name'],
    "RA":f"{ra_hours}:{ra_mins}:{round(ra_secs,6)}",
    "Dec":f"{dec_degs}:{dec_mins}:{round(dec_secs,6)}",
    "Transit":{"time":trans_time.utc_strftime("%Y-%m-%d %H:%M:%S"),"altitude":round(trans_alt,6)},
    "Times_at_35" : {"rise":rise35.utc_strftime("%Y-%m-%d %H:%M:%S"),"set":set35.utc_strftime("%Y-%m-%d %H:%M:%S"),"length":round(above35,6)},
    "Observable_time":round(t_obs,6)
    }

    all_dict[k["objid"]] = Toutput


output = {
"location":{"latitude":args.lat,"longitude":args.long,"elevation":args.elv},
"obs_date":today.strftime("%Y-%m-%d"),
"night_phases":{"sunset":sunset.utc_strftime("%Y-%m-%d %H:%M:%S"),"darktime-start":darkstart.utc_strftime("%Y-%m-%d %H:%M:%S"),"darktime-end":darkend.utc_strftime("%Y-%m-%d %H:%M:%S"),"sunrise":sunrise.utc_strftime("%Y-%m-%d %H:%M:%S")},
"moon":{"alt": round(malt,6), "phase-degs": round(mphase,6), "illumination-percent": round(mill,6)},
"targets":all_dict
}

#save output dict as json
with open('targets.json', 'w') as fp:
        json.dump(output, fp,indent=4)
