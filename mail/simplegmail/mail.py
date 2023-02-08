from simplegmail import Gmail
from datetime import datetime
import csv

#list of emails addresses to send the email to as CSV file
file=open("correspondents.csv")
correspondents = []
csvreader = csv.reader(file)
for row in csvreader:
    	correspondents.append(row[0]) #save all rows into a list
file.close()

#get dates from transient list
file=open("transient_list.csv")
csvreader = csv.reader(file) #openfile as csv
info = next(csvreader)[0] #save the dates on the first line
list_date = info[20:30] #date for which priority list was created
tns_date = info[-19:-9] #date of last update of TNS database
file.close()

date = datetime.now().strftime('%Y-%m-%d') #date to put in the subject

with open('email.txt', 'r') as file: #reads in text to put in body of the email
	words = file.read()

## notices to add to top of email if dates are not aligned ##
fault1, fault2 = False, False

if date != list_date: #notice at top of email if transient list is out of date
    fault1 = True
    notice1 = f"Please note: Transient list has not been updated since {list_date}<br>"
else:
    notice1 = ""

if date != tns_date: #notice at top of email if tns database is out of date
    fault2 = True
    notice2 = f"Please note: TNS database used is out of date (last updated on {tns_date})<br>"
else:
    notice2 = ""

if (fault1 or fault2) == True:
    notice = f"<p><font color=#FF0000><em> {notice1} {notice2} </em></font></p><hr>" #formatting notices
    words = notice+words #adding notices to top of email
else:
    words = words


gmail = Gmail() # will open a browser window to ask you to log in and authenticate

params = {
  "to": "bs.newtransients@gmail.com", #send to self
  "sender": "bs.newtransients@gmail.com",
  "bcc": correspondents, #bcc the correspondents so they can't see who else receives it
  "subject": f"Transients for {date}", #subject line with the date
  "msg_html": words, #html message from the text file
  "attachments": ["transient_list.csv"], #attaches the priority score list
  "signature": True  # use my account signature
}
message = gmail.send_message(**params) #sends email

print("Emails Sent.")
