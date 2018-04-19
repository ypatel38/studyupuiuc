from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse

from datetime import datetime, timedelta
from django.db import connection #sql
import json
# Create your views here.
class MapView(TemplateView):
    template_name = 'map/map.html'

    def get(self, request):
        
        cursor = connection.cursor()
        cursor.execute("SELECT home_studysession.building, home_studysession.date, home_studysession.start_time, home_studysession.end_time, home_studysession.seshID        \
                        FROM home_studysession")
        building_arr = cursor.fetchall()

        #now that we have every study_session ever, i need to populate the return dictionary

        building_dict = {}
        today = datetime.now().date()
        valid_sesh = []
        curr_time = datetime.now()
        for i in range(len(building_arr)):
            if building_arr[i][1] is None:
                continue
            #first test if session is on current date
            if (today - building_arr[i][1]).days == 0:
                #session is today
                #check if start time is in the past
                comb = datetime.combine(today, building_arr[i][2])
                if curr_time  >= comb:
                    #session has started
                    #check if it is still active, end time in future
                    comb = datetime.combine(today, building_arr[i][3])
                    if comb > curr_time:
                        #session is active, consider this tuple as a valid data point
                        if building_arr[i][0] not in building_dict:
                            building_dict[building_arr[i][0]] = {}
                            building_dict[building_arr[i][0]]['num_sesh'] = 1
                            building_dict[building_arr[i][0]]['num_students'] = 0
                            valid_sesh.append(building_arr[i][4])
                        else:
                            building_dict[building_arr[i][0]] += 1

        #now get number of students per a valid study session

        for i in valid_sesh:
            cursor.execute("SELECT  home_studysession.building, COUNT(home_sessionhas.netID)         \
                            FROM    home_studysession, home_sessionhas        \
                            WHERE   home_studysession.seshID = home_sessionhas.seshID AND      \
                                    home_studysession.seshID = %s       \
                            GROUP BY    home_studysession.building", [str(i)])
            temp_arr = cursor.fetchall()
            building_dict[temp_arr[0][0]]['num_students'] += temp_arr[0][1]
        print("FILTERED by ALL: ")
        print("Currently active study sessions: ")
        for i in building_dict.keys():
            print("There are", building_dict[i]['num_sesh'], "study sessions in", i, "with", building_dict[i]['num_students'], "students.")
            building_dict[i] = json.dumps(building_dict[i])
        building_dict = json.dumps(building_dict)






        #now i need to get the classes the user is in
        cursor.execute("SELECT 	accounts_enrolledin.class_code        \
                        FROM    accounts_enrolledin                 \
                        WHERE   accounts_enrolledin.netID = %s", [str(request.user)])
        middleman = cursor.fetchall()
        classes = []
        for i in range(len(middleman)):
            classes.append(middleman[i][0])


        classbuild_dict = {}
        #for each class, obtain relevant study sessions per building
        for curr_class in classes:
            #get buildings that have  to this class
            cursor.execute("SELECT   home_studysession.building, home_studysession.date, home_studysession.start_time, home_studysession.end_time, home_studysession.seshID        \
                            FROM     home_studysession, home_classofsession         \
                            WHERE    home_classofsession.seshID = home_studysession.seshID AND \
                                     home_classofsession.class_code = %s", [str(curr_class)])
            building_arr = cursor.fetchall()
            temp_dict = {}
            valid_sesh = []
            for i in range(len(building_arr)):
                if building_arr[i][1] is None:
                    continue
                #first test if session is on current date
                if (today - building_arr[i][1]).days == 0:
                    #session is today
                    #check if start time is in the past
                    comb = datetime.combine(today, building_arr[i][2])
                    if curr_time  >= comb:
                        #session has started
                        #check if it is still active, end time in future
                        comb = datetime.combine(today, building_arr[i][3])
                        if comb > curr_time:
                            #session is active, consider this tuple as a valid data point
                            if building_arr[i][0] not in temp_dict:
                                temp_dict[building_arr[i][0]] = {}
                                temp_dict[building_arr[i][0]]['num_sesh'] = 1
                                temp_dict[building_arr[i][0]]['num_students'] = 0
                                valid_sesh.append(building_arr[i][4])
                            else:
                                temp_dict[building_arr[i][0]] += 1

            #now get number of students per a valid study session

            for i in valid_sesh:
                cursor.execute("SELECT  home_studysession.building, COUNT(home_sessionhas.netID)         \
                                FROM    home_studysession, home_sessionhas        \
                                WHERE   home_studysession.seshID = home_sessionhas.seshID AND      \
                                        home_studysession.seshID = %s       \
                                GROUP BY    home_studysession.building", [str(i)])
                temp_arr = cursor.fetchall()
                temp_dict[temp_arr[0][0]]['num_students'] += temp_arr[0][1]

            #store this dict into classbuild dict
            classbuild_dict[curr_class] = temp_dict

        print("")
        print("FILTERED by CLASSES")
        for i in classbuild_dict.keys():
            print("")
            print("Currently active study sessions for", i, ":")
            for j in classbuild_dict[i].keys():
                print("There are", classbuild_dict[i][j]['num_sesh'], "study sessions in", j, "with", classbuild_dict[i][j]['num_students'], "students.")
                classbuild_dict[i][j] = json.dumps(classbuild_dict[i][j])
            classbuild_dict[i] = json.dumps(classbuild_dict[i])
        classbuild_dict = json.dumps(classbuild_dict)

        return render(request, self.template_name, {})

    def post(self, request):
        pass
