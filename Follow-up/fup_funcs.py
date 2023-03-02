"""
Functions that fup.py depends on to operate.

Author: George Hume
2023
"""

### IMPORTS ###
import csv
import numpy as np
import datetime as dt
import subprocess
from astropy import units as u
from astropy.coordinates import SkyCoord

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

    file=open(filename)
    csvreader = csv.reader(file) #openfile as csv
    date = next(csvreader) #save the date
    headers = next(csvreader) #save headers
    database = []
    for row in csvreader:
            database.append(row) #save all rows into a list
    #convert list into numpy array
    database = np.array(database,dtype="object")

    file.close()

    return date[0], headers, database

################################################################################

def tar_dicts(targets):
    """
    """

    #saves names and coords of top targets
    names = targets.T[1]+targets.T[2]
    RA = targets.T[3].astype(float)
    DEC = targets.T[4].astype(float)

    #convert all coords into a astropy coordinates object
    coords = SkyCoord(RA,DEC,unit="deg")

    #convert all coordinates into strings with units hmsdms
    cstr = coords.to_string("hmsdms")

    tars = [] #empty list to add dicts of targets names and coordinates to

    for i in range(names.size):

        #split apart the string to isolate ra and dec
        splt = cstr[i].index(" ")
        ra = list(cstr[i][0:splt-1])
        dec = list(cstr[i][splt+1:-1])

        #had to convert ra and dec into lists so could change the elements
        #chnaging from HhMmSs DdMmSs to H:M:S D:M:S as this is format ltrtml needs
        ra[2]=":"
        ra[5]=":"
        dec[3]=":"
        dec[6]=":"
        ra = "".join(ra)
        dec = "".join(dec)

        #add to list
        tars.append( {"name":names[i],"RA":ra,"DEC":dec} )

    return tars
