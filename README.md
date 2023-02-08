## Code for PHY61008 Project on doing follow-up observations of transient alerts.

List of directories:
- Visibility: Contains code that calculates the visibility of transients during a specified night given its right ascension and declination at the location of a follow-up telescope.
  - Version-Hist: Contains all previous versions of the visibility script.
- TNS: Contains code that automates the downloading of updates to the Transient Name Server (TNS) and then adds these updates to the TNS database saved on the local system. If run using cron tab this can update the local TNS database daily.
  - Checking: Contains scripts which can check if the locally updated TNS database matches with the official one.
- Filtering: Initally a combination of the Visibility and TNS directories that has been expanded upon. The code now automatically updates a local TNS database, filters it to remove older transients, and then calculates the priorty socres of these transients for the day in question using their brightnesses, observable times, times since detection, and lunar separations.
  - Version1: Contains the original version that was being used before February 2023.
- mail: This contains the code which can send out the transient lists produced by the code in the "Filtering" directory as daily emails.
  - simplegmail: method to send emails using the [simplegmail](https://github.com/jeremyephron/simplegmail) python package.
  - ssmtp: method to send emails using ssmtp and mailutils (method from [rianjs.net](https://rianjs.net/2013/08/send-email-from-linux-server-using-gmail-and-ubuntu-two-factor-authentication)).
