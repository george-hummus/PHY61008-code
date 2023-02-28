"""
Script to plot the visibility of the highest priorty transients on la Palma on the coming night.

Author: George Hume
2023
"""

### IMPORTS ###
import datetime as dt
from skyfield import almanac
from skyfield.api import N, E, wgs84, load, utc, Star
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import csv

# DATES #
today = dt.datetime.combine(dt.datetime.now(), dt.datetime.min.time()) + dt.timedelta(days=0.5)
today =today.replace(tzinfo=utc)
tomorrow = today + dt.timedelta(days=1) #next day at midday
tomorrow = tomorrow.replace(tzinfo=utc)

#location of Liverpool Telescope
lat = 28.6468866 #latitude in degs
long = -17.7742491 #longitude in degs
elv = 2326.0 #elevation in metres

### Set-up sky-field observing ##
location = wgs84.latlon(lat * N, long * E, elevation_m = elv) #location of observatory
ts = load.timescale() #loads in timescale
eph = load('de421.bsp')  #loads in ephemerides
#sets up sun, earth (needed for calculating dark time and our location respectivly) and moon (for illumination, etc.)
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']
Epos = earth + location #sets up observing position (i.e., the postion of the follow-up telescope)

#makes time objects from today and tomorrow
t0 = ts.from_datetime(today)
t1 = ts.from_datetime(tomorrow)

### Find the dark time start and end ###
f = almanac.dark_twilight_day(eph, location)
ts, events = almanac.find_discrete(t0, t1, f)

sunset = ts[0]
darkstart = ts[3]
darkend = ts[4]
sunrise = ts[7] #using the indcies to extract the different times of night

#set up figure
fig, ax = plt.subplots(1,2,figsize=(20,10))

lists = ["transient_list-F.csv", "transient_list-S.csv"]

for j, fname in enumerate(lists):
    ## format the plots ##
    ax[j].plot((sunset.utc_datetime(),sunrise.utc_datetime()),(0,0),color="grey",alpha=0.5,zorder=0) #horizon
    ax[j].plot((sunset.utc_datetime(),sunrise.utc_datetime()),(35,35),color="grey",alpha=0.5,zorder=0) #lower alt limit

    ax[j].vlines(darkstart.utc_datetime(), 0,90,color="grey",alpha=0.5,zorder=0)
    ax[j].vlines(darkend.utc_datetime(), 0,90,color="grey",alpha=0.5,zorder=0)
    ax[j].vlines(today + dt.timedelta(days=0.5), 0,90,color="grey",alpha=0.5,zorder=0)

    #annotations
    ax[j].annotate("End of Twilight", (darkstart.utc_datetime(),88),ha='center')
    ax[j].annotate("Start of Twilight", (darkend.utc_datetime(),88),ha='center')
    ax[j].annotate("Midnight", (today + dt.timedelta(days=0.5),88),ha='center')
    ax[j].annotate("Horizon", (sunset.utc_datetime(),1),(10,0),textcoords="offset pixels")
    ax[j].annotate("Airmass Lower Limit", (sunset.utc_datetime(),36),(10,0),textcoords="offset pixels")

    #backgrounds
    ax[j].axhspan(35, 0, facecolor='grey', alpha=0.2)
    ax[j].axhspan(0, -90, facecolor='grey', alpha=0.4)

    #formatting the plot
    xfmt = mdates.DateFormatter(' %H:%M')
    ax[j].xaxis.set_major_formatter(xfmt)
    ax[j].set_xlabel("UTC Time")
    ax[j].set_ylabel("Altitude (degrees)")
    ax[j].set_xlim((sunset.utc_datetime(),sunrise.utc_datetime()))
    ax[j].set_ylim(0,90)
    ax[j].set_title(f"Visibility of highest priority transients from {fname} during dark time on La Palma ({today.strftime('%Y-%m-%d')})")

    ax[j].grid(linestyle = ':')


    #ingest the Pscore File
    alerts=open(fname) #opens the csv file
    csvreader = csv.reader(alerts) #opens file as csv
    dummy = next(csvreader) #first row which is the date the CSV file was created
    dummy = next(csvreader) #second row contains the headers of the CSV file
    #now need to extract all the rows and save as numpy array
    rows = []
    for row in csvreader:
            rows.append(row)
    rows = np.array(rows,dtype="object")

    nrows = rows.shape[0] #number of rows in original list

    # check the number of rows in the pscore list
    if nrows > 5: #if over 5 pick the top 5
        top = rows[0:5]
    elif nrows != 0: #if less than 5 and greater than 0 then pick all
        top = rows[0:]
    else: #if no rows (blank list) then skip
        continue

    names = top.T[1]+top.T[2] #TNS name of each target
    RA = top.T[3].astype(float)/15 #convert to decimal hours
    dec = top.T[4].astype(float) #declination

    trows = top.shape[0] #number of rows in list of top entries

    talts = []
    for n in range(trows):
        tar =  Star(ra_hours=RA[n],dec_degrees=dec[n])

        Time = sunset

        altitudes = []
        times = []

        while Time.utc_datetime() < sunrise.utc_datetime():
            astro = Epos.at(Time).observe(tar)
            app = astro.apparent()
            #observers star at time from position

            alt, az, distance = app.altaz()

            altitudes.append(alt.degrees)
            times.append(Time.utc_datetime())

            Time += dt.timedelta(hours=0.1)

        talts.append(altitudes)

    for i in range(trows):
        ax[j].plot(times,talts[i],"--",label=names[i])

    ax[j].legend(loc='center left', bbox_to_anchor=(1, 0.5))


#save
plt.tight_layout()
plt.savefig(f"VisPlots/top_{today.strftime('%Y%m%d')}.jpg",dpi=600)
plt.close()
