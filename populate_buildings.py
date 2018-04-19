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

import pickle
from django.db import connection

data = pickle.load(open("addresses.p", "rb"))
cursor = connection.cursor()
attrs = ['instructor', 'location', 'time', 'type', 'day']

cursor.execute("DELETE FROM map_buildings")

for b, a in data:
    b = b.lower().title()
    a = a.lower().title()

    #sanitize here
    if (b == "Electrical And Computer Engineering"):
        b = "ECEB"
    elif (b == "Grainger Engineering Library Information Center"):
        b = "Grainger Engineering Library"


    cursor.execute("SELECT  map_buildings.building\
                    FROM    map_buildings \
                    WHERE   map_buildings.building = %s", [b])


    if(not cursor.fetchall() and b[0].isalpha()):
        cursor.execute("INSERT INTO map_buildings(building, \
                                                    address)\
                                            VALUES (%s,\
                                                    %s)",
                                                    [b, a])


cursor.close()
