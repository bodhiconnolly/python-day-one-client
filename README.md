A Python application that syncs with Dropbox to download your Day One entries and allows editing/adding of entries, including location and weather metadata using Google Maps and OpenWeatherMap.

#Setup
1. Install package prerequisites: 


-dropbox

-wx

-pygeocoder

-VideoCapture (Optional - Windows only)

2. Allow Dropbox access by running the dropbox_access.py file (using IDLE for this is easiest). This lets you authorise the app to access your entries and stores the auth token in settings.txt. 

3. Check the location of your Dropbox entries. Mine are in Dropbox\Apps\Day One\Journal.dayone\entries but I believe sometimes they are stored in Dropbox\Apps\Day One\Journal_dayone\entries instead. 
Make sure the location in settings.txt is correct for you. If you have no entries in the folder the app will crash and you will need to do a "fresh start".

4. To run the program, simply open day_one.py. The first time opening could be slow as it has to download all of the entry files. The terminal window will show progress during this time.

Bugs: I'm sure they exist - let me know!

To do a "fresh start", delete all files in the 'entries' 
and 'photos' folder, and delete all text in the 'cursor.txt' 
file. This will have been done on distribution.

Developed using Windows 8.1 and Python 2.7.6
by Bodhi Connolly in 2014 for CSSE1001