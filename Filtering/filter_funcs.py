"""
Functions thay filter.py depends on to operate.

Author: George Hume
2022
"""

### IMPORTS ###
import csv
import numpy as np
import datetime as dt

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
