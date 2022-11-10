## Code for PHY61008 Project on doing follow-up observations of transient alerts.

List of directories:
- Visibility: contains code that calculates the visibility of transients during a specified night given its right ascension and declination at the location of a follow-up telescope.
  - Version-Hist: contains all previous versions of the visibility script.
- TNS: contains code that automates the downloading of updates to the Transient Name Server (TNS) and then adds these updates to the TNS database saved on the local system. If run using cron tab this can update the local TNS database daily. 
  - Checking: contains scripts which can check if the locally updated TNS database matches with the official one.
- Filtering: a combination of the two other directories plus more. The code in this directory allows automatic updating of a local TNS database, filtering of the database to remove older transients, calculations of the observable time and lunar separation of the filtered transients, and finally the calculation of their priority scores.
