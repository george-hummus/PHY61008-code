from simplegmail import Gmail
from datetime import datetime
import csv

#list of emails addressses to send the email to as CSV file
file=open("correspondents.csv")
correspondents = []
csvreader = csv.reader(file)
for row in csvreader:
        correspondents.append(row[0]) #save all rows into a list
file.close()

date = datetime.now().strftime('%d/%m/%Y') #date to put in the subject

with open('email.txt', 'r') as file: #reads in text to put in body of the email
    words = file.read()

gmail = Gmail() # will open a browser window to ask you to log in and authenticate

params = {
  "to": "bs.newtransients@gmail.com",
  "sender": "bs.newtransients@gmail.com",
  "bcc": correspondents,
  "subject": f"Transients for {date}",
  "msg_plain": words,
  "attachments": ["transient_list.csv"],
  "signature": True  # use my account signature
}
message = gmail.send_message(**params)
