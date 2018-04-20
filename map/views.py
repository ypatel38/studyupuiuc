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
                            #get the corrdinates of this building
                            cursor.execute("SELECT  map_buildings.lat, map_buildings.lng    \
                                            FROM    map_buildings   \
                                            WHERE   map_buildings.building = %s", [building_arr[i][0]])
                            build = cursor.fetchall()
                            building_dict[building_arr[i][0]]['LatLng'] = {'Lat': build[0][0], 'Lng': build[0][1]}
                        else:
                            building_dict[building_arr[i][0]]['num_sesh'] += 1

        #now get number of students per a valid study session

        for i in valid_sesh:
            cursor.execute("SELECT  home_studysession.building, COUNT(home_sessionhas.netID)         \
                            FROM    home_studysession, home_sessionhas        \
                            WHERE   home_studysession.seshID = home_sessionhas.seshID AND      \
                                    home_studysession.seshID = %s       \
                            GROUP BY    home_studysession.building", [str(i)])
            temp_arr = cursor.fetchall()
            building_dict[temp_arr[0][0]]['num_students'] += temp_arr[0][1]


        #get the ranges for coloring purposes
        top = -1
        delta = 0
        #find smallest and largest weight
        for i in building_dict.keys():
            if building_dict[i]['num_sesh'] > top:
                top = building_dict[i]['num_sesh']

        #assign ranges for each section
        build_range_list = []
        #goes from the lowest bracket to the highest
        if top > 10:
            #use dynamic set up for greater than 10
            val = 1
            delta = int(top/5)-1
            remainder = top - (delta+1)*5
            for i in range(5):
                build_range_list.append({})
                build_range_list[i]['min'] = val
                build_range_list[i]['max'] = val + delta
                if remainder > 0:
                    build_range_list[i]['max'] += 1
                    val += delta + 2
                    remainder -= 1
                else:
                    val += delta + 1
        else:
            #use preset ranges
            for i in range(5):
                build_range_list.append({})
                build_range_list[i]['min'] = 1 + i*2
                build_range_list[i]['max'] = 2 + i*2

        build_range_list[4]['max'] = -1
        

        #assign range val to each building
        for i in building_dict:
            for j in range(5):
                print()
                if building_dict[i]['num_sesh'] >= build_range_list[j]['min'] and building_dict[i]['num_sesh'] <= build_range_list[j]['max']:
                    building_dict[i]['section'] = j
                    break


        print(build_range_list)
        print(building_dict)


        print("FILTERED by ALL: ")
        print("Currently active study sessions: ")
        for i in building_dict.keys():
            print("There are", building_dict[i]['num_sesh'], "study sessions in", i, "with", building_dict[i]['num_students'], "students.")
        building_dict = json.dumps(building_dict)

        


        #now i need to get the classes the user is in
        cursor.execute("SELECT     accounts_enrolledin.class_code        \
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
                                #get the corrdinates of this building
                                cursor.execute("SELECT  map_buildings.lat, map_buildings.lng    \
                                                FROM    map_buildings   \
                                                WHERE   map_buildings.building = %s", [building_arr[i][0]])
                                build = cursor.fetchall()
                                temp_dict[building_arr[i][0]]['LatLng'] = {'Lat': build[0][0], 'Lng': build[0][1]}
                            else:
                                temp_dict[building_arr[i][0]]['num_sesh'] += 1

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



        #find smallest and largest weight per class
        classbuild_range_list = {}
        for curr_class in classbuild_dict.keys():
            top = -1
            delta = 0
            #assign ranges for each section
            classbuild_range_list[curr_class] = []
            for i in classbuild_dict[curr_class]:
                if classbuild_dict[curr_class][i]['num_sesh'] > top:
                    top = classbuild_dict[curr_class][i]['num_sesh']
            if top > 10:
                #dynamic algorithm
                #goes from the lowest bracket to the highest
                val = 1
                delta = int(top/5)-1
                remainder = top - (delta+1)*5
                for i in range(5):
                    classbuild_range_list[curr_class].append({})
                    classbuild_range_list[curr_class][i]['min'] = val
                    classbuild_range_list[curr_class][i]['max'] = val + delta
                    if remainder > 0:
                        classbuild_range_list[curr_class][i]['max'] += 1
                        remainder -= 1
                        val += delta + 2
                    else:
                        val += delta + 1
            else:
                #preset splits
                for i in range(5):
                    classbuild_range_list[curr_class].append({})
                    classbuild_range_list[curr_class][i]['min'] = 1 + i*2
                    classbuild_range_list[curr_class][i]['max'] = 2 + i*2
            classbuild_range_list[curr_class][4]['max'] = -1
            #assign range val to each building
            for i in classbuild_dict[curr_class]:
                for j in range(5):
                    if classbuild_dict[curr_class][i]['num_sesh'] >= classbuild_range_list[curr_class][j]['min'] and classbuild_dict[curr_class][i]['num_sesh'] <= classbuild_range_list[curr_class][j]['max']:
                        classbuild_dict[curr_class][i]['section'] = j
                        break

        print(classbuild_dict)

        print("")
        print("FILTERED by CLASSES")
        for i in classbuild_dict.keys():
            print("")
            print("Currently active study sessions for", i, ":")
            for j in classbuild_dict[i].keys():
                print("There are", classbuild_dict[i][j]['num_sesh'], "study sessions in", j, "with", classbuild_dict[i][j]['num_students'], "students.")
        classbuild_dict = json.dumps(classbuild_dict)


        # find classes user is enrolled in
        cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                        FROM             accounts_enrolledin, \
                                         home_classes \
                        WHERE            %s = accounts_enrolledin.netID", [str(request.user)])

        #reorganize queryset to dict
        enrolledin_arr = cursor.fetchall()
        enrolledin = []
        for i in range(len(enrolledin_arr)):
            enrolledin.append({})
            enrolledin[i]['class_code'] = enrolledin_arr[i][0]

        cursor.close()

        args = {"enrolledin": enrolledin, "classbuild_dict": classbuild_dict, "classbuild_range_list": classbuild_range_list, "building_dict": building_dict, "build_range_list": build_range_list}

        return render(request, self.template_name, args)

    def post(self, request):
        pass
