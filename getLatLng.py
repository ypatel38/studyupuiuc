import requests
from django.db import connection
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studyupuiuc.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)



GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyAJ4C-DfepoKxXp8UtSZ4HgRmLX1NUBIp4'
max_lat = 40.117320
min_lat = 40.090995
max_lng = -88.209469
min_lng = -88.238754
#get all the buildings 
cursor = connection.cursor()
zero = 0.0
cursor.execute("SELECT	map_buildings.building, map_buildings.address 	\
				FROM 	map_buildings \
				WHERE 	map_buildings.lat = %s", [str(zero)])
building_arr = cursor.fetchall()

for i in building_arr:
	if i[1] is None:
		continue
	if i[1] == '' or i[1] == ' ':
		#no address, delete tuple
		print( "Empty address.    ", "Deleting", i[0])
		cursor.execute("DELETE FROM map_buildings \
						WHERE building = %s", [str(i[0])])
		continue
	params = {'address': i[1]}

	# Do the request and get the response data
	req = requests.get(GOOGLE_MAPS_API_URL, params=params)
	res = req.json()
	if res['status'] != 'OK':
		if res['status'] == 'ZERO_RESULTS':
			print(res['status'], ".    ", "Deleting", i[0])
			cursor.execute("DELETE FROM map_buildings \
						WHERE building = %s", [str(i[0])])
			continue
		print(res['status'])
		exit()
	else:
		# get lat and lng
		Lat = res['results'][0]['geometry']['location']['lat']
		Lng = res['results'][0]['geometry']['location']['lng']
		#make sure lat and lng are in bounds
		if Lat <= max_lat and Lat >= min_lat and Lng <= max_lng and Lng >= min_lng:
			#in range, update tuple
			cursor.execute("UPDATE 	map_buildings \
							SET 	lat = %s, lng = %s \
							WHERE	building = %s", [str(Lat), str(Lng), str(i[0])])
		else:
			#out of range, delete tuple
			print("Deleting", i[0])
			cursor.execute("DELETE FROM map_buildings \
							WHERE building = %s", [str(i[0])])
			continue



cursor.close()