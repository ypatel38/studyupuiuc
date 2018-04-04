#!/usr/bin/env python
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

data = pickle.load(open("alldata.p", "rb"))

attrs = ['instructor', 'location', 'time', 'type', 'day']

cursor = connection.cursor()

for dep in data.keys():
    for course in data[dep].keys():
        obj = data[dep][course]
        for crn in obj.keys():
            if(crn == 'name'):
                continue
            if(obj[crn]['time'] == 'ARRANGED'):
                obj[crn]['time'] = 'ARR-ANGED'
            cursor.execute("INSERT INTO home_section(crn, \
                                                    instructor, \
                                                    location, \
                                                    type, \
                                                    start_time, \
                                                    end_time, \
                                                    day)\
                                            VALUES (%s, \
                                                    %s, \
                                                    %s, \
                                                    %s, \
                                                    %s, \
                                                    %s, \
                                                    %s)",
                                                    [crn, obj[crn]['instructor'],\
                                                     obj[crn]['location'], obj[crn]['type'],\
                                                     obj[crn]['time'].split('-')[0],\
                                                     obj[crn]['time'].split('-')[1],\
                                                     obj[crn]['day']])

#print('Done')


cursor.close()
