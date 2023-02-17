"""
Script to plot the visibility of the top 5 priorty transients on la Palma on the coming night.

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


lists = ["transient_list-F.csv", "transient_list-S.csv"]

for fname in lists:
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

    top5 = rows[0:5]

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
    times, events = almanac.find_discrete(t0, t1, f)

    sunset = times[0]
    darkstart = times[3]
    darkend = times[4]
    sunrise = times[7] #using the indcies to extract the different times of night

    names = top5.T[1]+top5.T[2] #TNS name of each target
    RA = top5.T[3].astype(float)/15 #convert to decimal hours
    dec = top5.T[4].astype(float) #declination

    talts = []
    for n in range(5):
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

    #then lets plot the changing altitude of Betelgeuse during darktime
    fig, ax = plt.subplots(figsize=(10,10))
    for i in range(5):
        ax.plot(times,talts[i],"--",label=names[i])

    ax.plot(times,np.zeros(len(times)),color="grey",alpha=0.5,zorder=0) #horizon
    ax.plot(times,35*np.ones(len(times)),color="grey",alpha=0.5,zorder=0) #lower alt limit

    ax.vlines(darkstart.utc_datetime(), 0,90,color="grey",alpha=0.5,zorder=0)
    ax.vlines(darkend.utc_datetime(), 0,90,color="grey",alpha=0.5,zorder=0)
    ax.vlines(today + dt.timedelta(days=0.5), 0,90,color="grey",alpha=0.5,zorder=0)

    #annotations
    ax.annotate("End of Twilight", (darkstart.utc_datetime(),88),ha='center')
    ax.annotate("Start of Twilight", (darkend.utc_datetime(),88),ha='center')
    ax.annotate("Midnight", (today + dt.timedelta(days=0.5),88),ha='center')
    ax.annotate("Horizon", (sunset.utc_datetime(),1),(10,0),textcoords="offset pixels")
    ax.annotate("Airmass Lower Limit", (sunset.utc_datetime(),36),(10,0),textcoords="offset pixels")

    #backgrounds
    ax.axhspan(35, 0, facecolor='grey', alpha=0.2)
    ax.axhspan(0, -90, facecolor='grey', alpha=0.4)

    #formatting the plot
    xfmt = mdates.DateFormatter(' %H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    ax.set_xlabel("UTC Time")
    ax.set_ylabel("Altitude (degrees)")
    ax.set_xlim([times[0],times[-1]])
    ax.set_ylim(0,90)
    ax.set_title(f"Visibility of top 5 targets from {fname} during dark time on La Palma ({today.strftime('%Y-%m-%d')})")

    plt.grid(linestyle = ':')

    #display
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(f"VisPlots/top5_{fname[-5:-4]}_{today.strftime('%Y%m%d')}.jpg",dpi=600)
    plt.close()
