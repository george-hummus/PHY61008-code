"""
Functions thay filter.py depends on to operate.

Author: George Hume
2022
"""

### IMPORTS ###
import csv
import numpy as np
import datetime as dt
from skyfield import almanac
from skyfield.api import N, E, wgs84, load, utc, Star

################################################################################

def loadDB(filename):
    """
    Function to load in the TNS database from its CSV file
    Arguments:
        - filename: A string representing file name of the TNS database (usually 'tns_public_objects.csv')
    Outputs:
        - date: the date the TNS database was updated as a string in the format '%Y-%m-%d %H:%M:%S'
        - headers: the first row of the database containing the column headers as a list
        - database: numpy object array containg all the entries of the TNS database
    """

    file=open(filename) #database released on 2022-10-11 00:00:00
    csvreader = csv.reader(file) #openfile as csv
    date = next(csvreader) #save the date
    headers = next(csvreader) #save headers
    database = []
    for row in csvreader:
            database.append(row) #save all rows into a list
    #convert list into numpy array
    database = np.array(database,dtype="object")

    return date[0], headers, database

################################################################################

def TNSlice(database,date):
    """
    Function that slices the TNS database so only the transients discovered in the last 3 months
    and modified in the last 2 weeks are left.
    Arguments:
        - database: numpy object array contining the TNS database
        - date: string representing the date that the TNS database was released (in format '%Y-%m-%d %H:%M:%S')
    Outputs:
        - sliceDB: numpy object array of the sliced TNS database
    """

    #extract the time modified and the time discovered
    t_mod = database.T[-1]
    t_disc = database.T[12]

    #convert the date csv was released as datetime object
    rdate = dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    #datetime limits for the time modified and time discovered
    fortnight = rdate - dt.timedelta(weeks=2) #2 weeks ago
    threemonths = rdate - dt.timedelta(weeks=12) #3 months ago (or 12 weeks)

    good_tars = [] #empty list to save rows which pass the slicing to

    for i in range(t_mod.size):
        #convert times to datetime objects
        tMOD = dt.datetime.strptime(t_mod[i], '%Y-%m-%d %H:%M:%S')
        tDISC = dt.datetime.strptime(t_disc[i][:-4], '%Y-%m-%d %H:%M:%S')
        #slice [:-4] is to remove fractions of secs

        #if the discovery date is less than 3 months ago then can include
        if tDISC > threemonths:
            #if the time modified is less than a fortnight ago then can add it to new array
            if tMOD > fortnight:
                good_tars.append(database[i])

    sliceDB = np.array(good_tars,dtype=object)

    return sliceDB

################################################################################

def Visibility(date, ra, dec, lat, long, elv):
    """
    Function that calaculates the observable time, lunar separation and transit altitude
    of a list of targets given their right ascension and declination, the latitude
    longitude and elevation of the elevation, and the date of the start of the night.
    Arguments:
        - date: string of the date of observation (in format '%Y-%m-%d %H:%M:%S')
        - ra: list of right ascensions of the targets (in decimal degrees)
        - dec: list of declinations of the targets (in decimal degrees)
        - lat: the latitude of the location (in decimal degrees)
        - long: the eastwards longitude of the location (in decimal degrees)
        - elv: the elevation of the location (in metres)
    Outputs:
        - tObs: the time in hours that the target is above 35 altitude in dark time
        - tAlt: the altitude of the target when it transits the meridian (in decimal degrees)
        - lSep: the average separation between the moon and the target during the night (in decimal degrees)
    """

    #convert date to datetime object at midday
    today = dt.datetime.strptime(date, '%Y%m%d') + dt.timedelta(days=0.5)
    today =today.replace(tzinfo=utc)
    tomorrow = today + dt.timedelta(days=1) #next day at midday
    tomorrow = tomorrow.replace(tzinfo=utc)


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

    #find the UTC time at the middle of the night
    middark = ts.from_datetime(darkstart.utc_datetime()+((darkend.utc_datetime() - darkstart.utc_datetime())/2))
    darktimes = [darkstart,middark,darkend] #list of the time at the start, middle, and end of dark time

    ## calculate moon's alt, phase, and illumination ##
    midnight = t0 + dt.timedelta(hours=12)
    mastro = Epos.at(midnight).observe(moon)
    mapp = mastro.apparent()
    malt, maz, mdst = mapp.altaz()
    mphase = almanac.moon_phase(eph, t0)
    mill = almanac.fraction_illuminated(eph,"moon",midnight)
    malt, mphase = malt.degrees, mphase.degrees

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
        Function that calculates the absolute value of the hour angle of a target for at a specified altitude, given the latitude of the location and the declination of the target.
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

    ## CALCULATING OUTPUTS ##
    #empty lists to fill
    tObs, tAlt, lSep = [], [], []

    #find altitude of each transient at sunset, start of dark time, end of darktime, and sunrise
    for k in range(ra.size):
        #RA and Dec of target in decimal degrees
        RA = ra[k]
        Dec = dec[k]

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

            if t_obs > 0: #if non zero time for observing then can calculate the lunar separation
                a_seps = []
                for DT in darktimes:
                    # angular separation doesn't depend on location on earth just time
                    e = earth.at(DT) #set earth as centre
                    m = e.observe(moon) #observe moon at time DT
                    T = e.observe(target) #observe target at time DT
                    a_sep = m.separation_from(T).degrees #find angular separation in degrees
                    a_seps.append(a_sep) #append to list

                asep = np.mean(a_seps) #find mean angular separation during darktime

            else: #if no observable time then don't need to calculate the angular sep
                asep = 0

        # add to the lists
        tObs.append(t_obs)
        tAlt.append(trans_alt)
        lSep.append(asep)

    #return and convert to numpy arrays
    return np.array(tObs), np.array(tAlt), np.array(lSep)

################################################################################

def pscore(database,weights):
    """
    Filters a database of targets by removing all those with zero observable time
    and then calculates the rest's priorty score, which depends on the target's
    ranking in observable time, transit altitude, and lunar separation.
    The filtered database is then saved  as a numpy array with the priorty
    scores as the final column.
    Arguments:
        - database: numpy object array of the list of targets (ID first column and the observable time, transit altitude, and lunar separation in last 3 columns)
        - weights: list of numbers to weight the contribitions towards the priorty score for the  observable time, transit altitude, and lunar separation
    Outputs:
        - t_targets: new numpy object array with the remaning targets and their priorty scores in the final column
    """

    #remove all entries which are not observable
    bad_idx = []
    for i in range(database.shape[0]):
        if t_array[i][-3] == 0: #check the observable time of the target
            bad_idx.append(i)
    t_array = np.delete(database,bad_idx,0) #deletes rows with no observable time

    #save remaning IDs
    newIDs = t_array.T[0]
    pscores = np.zeros(newIDs.shape)

    #sort the intresting rows in acending order
    to_sort = np.sort(t_array.T[-3])
    ms_sort = np.sort(t_array.T[-1])
    alt_sort = np.sort(t_array.T[-2])

    #ranking loop - may need a better way to rank these
    for j in range(to_sort.size):
        #extracts the value of the sorted arrays
        to = to_sort[j]
        ms = ms_sort[j]
        al = alt_sort[j]

        #looks for the indices of the rows these values correpsonds to in the array of targets
        tID = np.where(t_array.T[-3]==to)[0]
        mID = np.where(t_array.T[-1]==ms)[0][0]
        aID = np.where(t_array.T[-2]==al)[0][0]

        #adds the value of j to priorty score for the given index - weighted
        pscores[tID] += (weights[0]*j)
        pscores[mID] += (weights[1]*j)
        pscores[aID] += (weights[2]*j)

    #add the priorty scores to the new database array
    t_targets = np.append(t_targets,pscores.resize(pscores.size,1),axis=1)

    return t_targets

################################################################################

def flatten(l):
    "Flattens a list of lists, l"
    return [item for sublist in l for item in sublist]

################################################################################
