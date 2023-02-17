# Code using in Master's Project regarding automating follow-up observations of transients for the PEPPER Survey on the Liverpool Telescope.

## List of directories:

- ### Visibility:

    Contains code that calculates the visibility of transients during a specified night given its right ascension and declination at the location of a follow-up telescope.

  - Version-Hist: Contains all previous versions of the visibility script.


- ### TNS:

    Contains code that automates the downloading of updates to the Transient Name Server (TNS) and then adds these updates to the TNS database saved on the local system. If run using cron tab this can update the local TNS database daily.

  - Checking: Contains scripts which can check if the locally updated TNS database matches with the official one.


- ### Filtering:
    Initally a combination of the Visibility and TNS directories that has been expanded upon. The code now automatically updates a local TNS database, filters it to remove older transients, and then calculates the priorty socres of these transients for the day in question using their brightnesses, observable times, times since detection, and lunar separations.
  - Version1: Contains the original version that was being used before February 2023.
  - Version2: Contains the 2nd version of the code that was being used in the beginning of February 2023.


- ### mail:

    This contains the code which can send out the transient lists produced by the code in the "Filtering" directory as daily emails.
  - simplegmail: method to send emails using the [simplegmail](https://github.com/jeremyephron/simplegmail) python package.
  - ssmtp: method to send emails using ssmtp and mailutils (method from [rianjs.net](https://rianjs.net/2013/08/send-email-from-linux-server-using-gmail-and-ubuntu-two-factor-authentication)).


- ### FastSlow:
    A new form of the code package that updates the local TNS database, creates the priority list and sends the daily emails. The main new addition is that two lists are created for the PEPPER Fast and Slow surveys, where the targets used come from a different time frames and the priority score weightings are different. The method of sending emails has also changed now using a method from [mailtrap.io](https://mailtrap.io/blog/python-send-email-gmail/) to avoid the manual re-authentication needed with simplegmail. Additionally, the email now includes a HTML table of the Fast list with clickable links to view the targets in the TNS or Fink broker.
