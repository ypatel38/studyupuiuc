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

data = pickle.load(open("class_name.p", "rb"))
cursor = connection.cursor()
attrs = ['instructor', 'location', 'time', 'type', 'day']
for dep in data.keys():
    for course in data[dep].keys():
        #obj = data[dep][course]
        #print(course)
        if(course != 'link' and 'name' in data[dep][course].keys()):
            cursor.execute("INSERT INTO home_classes(class_code, \
		                                                class_name)\
		                                        VALUES (%s,\
		                                                %s)",
		                                                [course.replace(" ", ""), data[dep][course]['name']])

cursor.close()
