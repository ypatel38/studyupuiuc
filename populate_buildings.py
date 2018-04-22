import os
import sys

# RUN THIS BEFORE getLatLong.py

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
    elif (b == "Ymca"):
        b = "YMCA"
    elif (b == "Aces Library, Info. & Alumni Center"):
        b = "ACES Library, Info. & Alumni Center"
    elif (b == "Admissions And Records Building"):
        b = "Admissions and Records Building"
    elif (b == "Agronomy Field Laboratory-Usda"):
        b = "Agronomy Field Laboratory-USDA"
    elif (b == "Art And Design Building"):
        b = "Art and Design Building"
    elif (b == "Center For Wounded Veterans In Higher Education"):
        b = "Center For Wounded Veterans in Higher Education"
    elif (b == "College Of Fine And Applied Arts Performing Arts Annex"):
        b = "College of Fine and Applied Arts Performing Arts Annex"
    elif (b == "Dalkey Archive Press(Pssb)"):
        b = "Dalkey Archive Press(PSSB)"
    elif (b == "Institute For Genomic Biology"):
        b == "Institute for Genomic Biology"
    elif (b == "Irwin Center For Doctoral Study In Business"):
        b = "Irwin Center for Doctoral Study in Business"
    elif (b == "Library And Information Science Bldg"):
        b = "Library and Information Science Bldg"
    elif (b == "Loomis Laboratory Of Physics"):
        b = "Loomis Laboratory of Physics"
    elif (b == "Materials Science And Eng Bldg"):
        b = "Materials Science and Eng Bldg"
    elif (b == "Micro And Nanotechnology Laboratory"):
        b = "Micro and Nanotechnology Laboratory"
    elif (b == "National Center For Supercomputing Applications"):
        b = "National Center for Supercomputing Applications"
    elif (b == "Noyes Laboratory Of Chemistry"):
        b = "Noyes Laboratory of Chemistry"
    elif (b == "Optical Physics And Engineering Bldg"):
        b = "Optical Physics and Engineering Bldg"
    elif (b == "Siebel Center For Computer Science"):
        b = "Siebel Center for Computer Science"
    elif (b == "Speech And Hearing Science"):
        b = "Speech and Hearing Science Building"
    elif (b == "Student Dining And Residential Programs Building"):
        b = "Student Dining and Residential Programs Building"
    elif (b == "Technical Development And Fabrication Center lii"):
        b = "Technical Development and Fabrication Center"
    elif (b == "Townsend Hall - Isrh"):
        b = "Townsend Hall - ISR"
    elif (b == "Trelease Hall - Farh"):
        b = "Trelease Hall Hall - FAR"
    elif (b == "Wardall Hall - Isrh"):
        b = "Wardall Hall - ISR"
    elif (b == "College Of Fine And Applied Arts Performing Arts Annex"):
        b = "College of Fine and Applied Arts Performing Arts Annex"


    cursor.execute("SELECT  map_buildings.building\
                    FROM    map_buildings \
                    WHERE   map_buildings.building = %s", [b])


    if((not cursor.fetchall()) and b[0].isalpha()):
        cursor.execute("INSERT INTO map_buildings(building, \
                                                  address, \
                                                  lat, \
                                                  lng)\
                                            VALUES (%s,\
                                                    %s, \
                                                    0, \
                                                    0)",
                                                    [b, a])


cursor.close()
