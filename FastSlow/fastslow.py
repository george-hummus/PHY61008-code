"""
Script to filter targets from the TNS database, calaculate how long they're visible for on the night
in question and uses this information along with their transit altitude, lunar separation, time
discovered, time modified, and magnitude to calculate a priorty score for observing them with the
Liverpool Telescope on La Palma, España.
Produces two priority lists taliored to the aims of the PEPPER Fast and Slow surveys.

Depends on functions.py script to operate.

Author: George Hume
2023
"""

### IMPORTS ###
import csv
import numpy as np
import datetime as dt
from functions import *
import pandas as pd

# loads in the tns database as numpy array along with the date it was released as a string and a list of the headers
date, headers, database = loadDB("/home/pha17gh/TNS/tns_public_objects.csv")
#create a new list of headers for the new database (as have removed columns and added new ones)
newHeaders = flatten([headers[0:5], [headers[12], headers[-1],headers[13], "observable_time", "lunar_sep", "priority_score", "fink_url"]])

#line to go before headers to give context in CSV
Tday = dt.datetime.combine(dt.datetime.now(), dt.datetime.min.time()) #today's data at turn of the day
todaySTR = Tday.strftime('%Y-%m-%d %H:%M:%S')
topline = [f"List calculated for {todaySTR} using TNS database from {date}"]


# PEPPER FAST #
fastDB = priority_list(database,date,False)

#save out fast database CSV
filename = "/home/pha17gh/TNS/transient_list-F.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow(topline)
    csvwriter.writerow(newHeaders) #add headers first row
    csvwriter.writerows(fastDB) # write the rest of the data

if fastDB.size == 0:
    #if no transients met the requirements replace table with notice
    file = open("/home/pha17gh/TNS/mail/transient_list-F.html", "w")
    file.write("<p><font color=#FF0000><em> No transients met the requirements for PEPPER Fast tonight. </em></font></p><br>")
else:
    #save out fast database as HTML table to attach to email
    #render dataframe as html file
    df = pd.DataFrame(fastDB, columns = newHeaders)
    df['fink_url'] = '<a href=' + df['fink_url'] + '><div>' + df['fink_url'] +'</div></a>' #makes fink url clickable
    df['name'] = '<a href=' + "https://www.wis-tns.org/object/" + df['name'] + '><div>' + df['name'] +'</div></a>' #click tns name to take to website
    html = df.to_html(escape=False, justify = "left",index = False)
    file = open("/home/pha17gh/TNS/mail/transient_list-F.html", "w")
    file.write(html)


# PEPPER SLOW #
slowDB = priority_list(database,date)

if slowDB.size == 0:
    #if no transients met the requirements for slow then they didn't for fast either
    # so can add message explaining none met slow requirements either
    file.write("<p><font color=#FF0000><em> No transients met the requirements for PEPPER Slow tonight. </em></font></p><br>")

file.close()

#save out the slow database CSV
filename = "/home/pha17gh/TNS/transient_list-S.csv"
with open(filename, 'w') as file:
    csvwriter = csv.writer(file,delimiter=",") # create a csvwriter object
    csvwriter.writerow(topline)
    csvwriter.writerow(newHeaders) #add headers first row
    csvwriter.writerows(slowDB) # write the rest of the data
