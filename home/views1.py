from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.db import connection #sql
from django.urls import reverse #used for namespaces
from home.forms import *
from datetime import datetime, timedelta
import operator, json, re

# Create your views here.

class HomeView(TemplateView):
    template_name = "home/homepage.html"



    def get(self, request):
        #sql query's here to get all info and put into args (temp)
        #TODO: THIS QUERY IS TEMPORARY FOR A TEST, NEEDS TO BE CLEANED UP WITH SORTS, ORGANIZED ARGS, ETC!!!


        # find session corresponding to users enrolled ClassOfSession
        cursor = connection.cursor()
        cursor.execute("SELECT      home_studysession.start_time, \
                                    home_studysession.end_time, \
                                    home_studysession.date, \
                                    home_studysession.building, \
                                    home_studysession.room_number, \
                                    home_studysession.description, \
                                    home_studysession.seshID, \
                                    home_classes.class_code, \
                                    home_classes.class_name \
                        FROM        accounts_enrolledin, \
                                    home_classes, \
                                    home_classofsession, \
                                    home_studysession \
                        WHERE       accounts_enrolledin.netID = %s AND \
                                    accounts_enrolledin.class_code = home_classes.class_code AND \
                                    home_classes.class_code = home_classofsession.class_code AND \
                                    home_classofsession.seshID = home_studysession.seshID \
                        ORDER BY    date(home_studysession.date), \
                                    time(home_studysession.start_time), \
                                    time(home_studysession.end_time), \
                                    home_studysession.building, \
                                    home_studysession.room_number", [str(request.user)])

        sessions_arr = cursor.fetchall()

        #print(sessions_arr[0][2])
        #print(sessions_arr[0][1])
        #print(type(sessions_arr[0][2]))
        #print(type(sessions_arr[0][1]))
        #print(datetime.now().date())
        #print(datetime.now().time())
        #print(sessions_arr)
        #reorganize queryset to dict
        sessions = []
        count = 0;
        for i in range(len(sessions_arr)):
            if(sessions_arr[i] is None):
                continue;
            #check if session is sceduled for adf
            if(datetime.now().date() < sessions_arr[i][2]) or ((datetime.now().date() == sessions_arr[i][2]) and (datetime.now().time() < sessions_arr[i][1])):
                sessions.append({})
                sessions[count]['start_time'] = sessions_arr[i][0]
                sessions[count]['end_time'] = sessions_arr[i][1]
                sessions[count]['date'] = sessions_arr[i][2]
                sessions[count]['building'] = sessions_arr[i][3]
                sessions[count]['room_number'] = sessions_arr[i][4]

                hasData = False
                for j in range(len(sessions_arr[i][5])):
                    if sessions_arr[i][5][j] != " ":
                        hasData = True
                        break
                if hasData:
                    sessions[count]['description'] = sessions_arr[i][5]
                else:
                    sessions[count]['description'] = ""

                sessions[count]['seshID'] = sessions_arr[i][6]
                sessions[count]['class_code'] = sessions_arr[i][7]
                sessions[count]['class_name'] = sessions_arr[i][8]
                count+=1

        #print(sessions)

        cursor.execute("SELECT      home_sessionhas.is_owner, \
                                    home_studysession.seshID \
                        FROM        accounts_enrolledin, \
                                    home_classes, \
                                    home_classofsession, \
                                    home_studysession, \
                                    home_sessionhas \
                        WHERE       accounts_enrolledin.netID = %s AND \
                                    home_sessionhas.netID = accounts_enrolledin.netID AND \
                                    accounts_enrolledin.class_code = home_classes.class_code AND \
                                    home_classes.class_code = home_classofsession.class_code AND \
                                    home_classofsession.seshID = home_studysession.seshID AND \
                                    home_classofsession.seshID = home_sessionhas.seshID", [str(request.user)])

        sessions_arr = cursor.fetchall()
        #print(sessions_arr)

        for i in range(len(sessions)):
            sessions[i]['is_owner'] = 0
            sessions[i]['is_joined'] = 0
        for i in range(len(sessions_arr)):
            for j in range(len(sessions)):
                if(sessions[j]['seshID'] == sessions_arr[i][1]):
                    sessions[j]['is_owner'] = sessions_arr[i][0]
                    sessions[j]['is_joined'] = 1




        # find classes user is enrolled in and are empty
        cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                        FROM             accounts_enrolledin \
                        WHERE            %s = accounts_enrolledin.netID AND \
                                         accounts_enrolledin.class_code IN( \
                                            SELECT DISTINCT home_classofsession.class_code \
                                            FROM home_studysession, home_classofsession \
                                            WHERE home_studysession.seshID = home_classofsession.seshID)", [str(request.user)])

        #reorganize queryset to dict
        enrolledin_empty_arr = cursor.fetchall()
        enrolledin_empty = []
        for i in range(len(enrolledin_empty_arr)):
            enrolledin_empty.append(enrolledin_empty_arr[i][0])


        # find classes user is enrolled in
        cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                        FROM             accounts_enrolledin, \
                                         home_classes \
                        WHERE            accounts_enrolledin.netID = %s", [str(request.user)])

        #reorganize queryset to dict
        enrolledin_arr = cursor.fetchall()
        enrolledin = []
        for i in range(len(enrolledin_arr)):
            enrolledin.append({})
            enrolledin[i]['class_code'] = enrolledin_arr[i][0]
            if(enrolledin[i]['class_code'] in enrolledin_empty):
                enrolledin[i]['class_empty'] = False
            else:
                enrolledin[i]['class_empty'] = True


        # find number of sessions joined by the user
        cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                        FROM             home_studysession, \
                                         home_sessionhas \
                        WHERE            %s = home_sessionhas.netID AND \
                                         home_studysession.seshID = home_sessionhas.seshID", [str(request.user)])

        #reorganize queryset to dict
        sessions_joined_arr = cursor.fetchall()
        sessions_joined = 0
        sessions_joined = sessions_joined_arr[0][0]

        # find number of sessions created by the user
        cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                        FROM             home_studysession, \
                                         home_sessionhas \
                        WHERE            %s = home_sessionhas.netID AND \
                                         home_studysession.seshID = home_sessionhas.seshID AND \
                                         %s = home_sessionhas.is_owner", [str(request.user), True])

        #reorganize queryset to dict
        sessions_created_arr = cursor.fetchall()
        sessions_created = 0
        sessions_created = sessions_created_arr[0][0]

        connection.close()

        #print(sessions)
        args = {'sessions': sessions, 'enrolledin': enrolledin, 'sessions_joined': sessions_joined, 'sessions_created': sessions_created}
        #print(sessions)
        return render(request, self.template_name, args)


    def post(self, request):
        #print("HELLO")
        #print(request.POST)
        if("edit" in request.POST):
            seshID = request.POST["edit"]
            function = "edit"
        elif("delete" in request.POST):
            seshID = request.POST["delete"]
            function = "delete"
        else:
            seshID = request.POST["seshID"]
            function = request.POST["function"]

        if function == "is_joined":
            is_joined  = str(request.POST["is_joined"])

            #print(is_joined)
            #print(seshID)
            cursor = connection.cursor()

            if (is_joined == "1"):
                cursor.execute("INSERT INTO      home_sessionhas(seshID, netID, is_owner) \
                                VALUES           (%s, %s, 0)", [seshID, str(request.user)])
            else:

                cursor.execute("DELETE FROM      home_sessionhas  \
                                WHERE            home_sessionhas.netID = %s AND\
                                                 home_sessionhas.is_owner = 0 AND \
                                                 home_sessionhas.seshID = %s", [str(request.user), seshID])

            #GET REQUEST
            # find session corresponding to users enrolled ClassOfSession
            cursor = connection.cursor()
            cursor.execute("SELECT      home_studysession.start_time, \
                                        home_studysession.end_time, \
                                        home_studysession.date, \
                                        home_studysession.building, \
                                        home_studysession.room_number, \
                                        home_studysession.description, \
                                        home_studysession.seshID, \
                                        home_classes.class_code, \
                                        home_classes.class_name \
                            FROM        accounts_enrolledin, \
                                        home_classes, \
                                        home_classofsession, \
                                        home_studysession \
                            WHERE       accounts_enrolledin.netID = %s AND \
                                        accounts_enrolledin.class_code = home_classes.class_code AND \
                                        home_classes.class_code = home_classofsession.class_code AND \
                                        home_classofsession.seshID = home_studysession.seshID \
                            ORDER BY    datetime(home_studysession.date), \
                                        datetime(home_studysession.start_time), \
                                        datetime(home_studysession.end_time), \
                                        home_studysession.building, \
                                        home_studysession.room_number", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)
            #reorganize queryset to dict
            sessions = []
            count = 0;
            for i in range(len(sessions_arr)):
                #check if session is sceduled for adf
                if(datetime.now().date() < sessions_arr[i][2]) or ((datetime.now().date() == sessions_arr[i][2]) and (datetime.now().time() < sessions_arr[i][1])):
                    sessions.append({})
                    sessions[count]['start_time'] = sessions_arr[i][0]
                    sessions[count]['end_time'] = sessions_arr[i][1]
                    sessions[count]['date'] = sessions_arr[i][2]
                    sessions[count]['building'] = sessions_arr[i][3]
                    sessions[count]['room_number'] = sessions_arr[i][4]
                    sessions[count]['description'] = sessions_arr[i][5]
                    sessions[count]['seshID'] = sessions_arr[i][6]
                    sessions[count]['class_code'] = sessions_arr[i][7]
                    sessions[count]['class_name'] = sessions_arr[i][8]
                    count+=1

            cursor.execute("SELECT      home_sessionhas.is_owner, \
                                        home_studysession.seshID \
                            FROM        accounts_enrolledin, \
                                        home_classes, \
                                        home_classofsession, \
                                        home_studysession, \
                                        home_sessionhas \
                            WHERE       accounts_enrolledin.netID = %s AND \
                                        home_sessionhas.netID = accounts_enrolledin.netID AND \
                                        accounts_enrolledin.class_code = home_classes.class_code AND \
                                        home_classes.class_code = home_classofsession.class_code AND \
                                        home_classofsession.seshID = home_studysession.seshID AND \
                                        home_classofsession.seshID = home_sessionhas.seshID", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)

            for i in range(len(sessions)):
                sessions[i]['is_owner'] = 0
                sessions[i]['is_joined'] = 0
            for i in range(len(sessions_arr)):
                for j in range(len(sessions)):
                    if(sessions[j]['seshID'] == sessions_arr[i][1]):
                        sessions[j]['is_owner'] = sessions_arr[i][0]
                        sessions[j]['is_joined'] = 1

            # find classes user is enrolled in and are empty
            cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                            FROM             accounts_enrolledin \
                            WHERE            %s = accounts_enrolledin.netID AND \
                                             accounts_enrolledin.class_code IN( \
                                                SELECT DISTINCT home_classofsession.class_code \
                                                FROM home_studysession, home_classofsession \
                                                WHERE home_studysession.seshID = home_classofsession.seshID)", [str(request.user)])

            #reorganize queryset to dict
            enrolledin_empty_arr = cursor.fetchall()
            enrolledin_empty = []
            for i in range(len(enrolledin_empty_arr)):
                enrolledin_empty.append(enrolledin_empty_arr[i][0])


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
                if(enrolledin[i]['class_code'] in enrolledin_empty):
                    enrolledin[i]['class_empty'] = False
                else:
                    enrolledin[i]['class_empty'] = True


            # find number of sessions joined by the user
            cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                            FROM             home_studysession, \
                                             home_sessionhas \
                            WHERE            %s = home_sessionhas.netID AND \
                                             home_studysession.seshID = home_sessionhas.seshID", [str(request.user)])

            #reorganize queryset to dict
            sessions_joined_arr = cursor.fetchall()
            sessions_joined = 0
            sessions_joined = sessions_joined_arr[0][0]

            # find number of sessions created by the user
            cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                            FROM             home_studysession, \
                                             home_sessionhas \
                            WHERE            %s = home_sessionhas.netID AND \
                                             home_studysession.seshID = home_sessionhas.seshID AND \
                                             home_sessionhas.is_owner = 0", [str(request.user)])

            #reorganize queryset to dict
            sessions_created_arr = cursor.fetchall()
            sessions_created = 0
            sessions_created = sessions_created_arr[0][0]

            connection.close()

            #print(sessions)
            args = {'sessions': sessions, 'enrolledin': enrolledin, 'sessions_joined': sessions_joined, 'sessions_created': sessions_created}
            #print(sessions)
            return render(request, self.template_name, args)


        elif function == "delete":
            cursor = connection.cursor()

            cursor.execute("SELECT           home_sessionhas.netID  \
                            FROM             home_sessionhas \
                            WHERE            home_sessionhas.netID = %s AND\
                                             home_sessionhas.is_owner = 1 AND \
                                             home_sessionhas.seshID = %s", [str(request.user), seshID])


            is_valid_delete = cursor.fetchall()

            if is_valid_delete:
                cursor.execute("DELETE FROM      home_studysession \
                                WHERE            home_studysession.seshID = %s", [seshID])
                cursor.execute("DELETE FROM      home_sessionhas \
                                WHERE            home_sessionhas.seshID =  %s", [seshID])
                cursor.execute("DELETE FROM      home_classofsession \
                                WHERE            home_classofsession.seshID = %s", [seshID])

            #GET REQUEST
            # find session corresponding to users enrolled ClassOfSession
            cursor = connection.cursor()
            cursor.execute("SELECT      home_studysession.start_time, \
                                        home_studysession.end_time, \
                                        home_studysession.date, \
                                        home_studysession.building, \
                                        home_studysession.room_number, \
                                        home_studysession.description, \
                                        home_studysession.seshID, \
                                        home_classes.class_code, \
                                        home_classes.class_name \
                            FROM        accounts_enrolledin, \
                                        home_classes, \
                                        home_classofsession, \
                                        home_studysession \
                            WHERE       accounts_enrolledin.netID = %s AND \
                                        accounts_enrolledin.class_code = home_classes.class_code AND \
                                        home_classes.class_code = home_classofsession.class_code AND \
                                        home_classofsession.seshID = home_studysession.seshID \
                            ORDER BY    datetime(home_studysession.date), \
                                        datetime(home_studysession.start_time), \
                                        datetime(home_studysession.end_time), \
                                        home_studysession.building, \
                                        home_studysession.room_number", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)
            #reorganize queryset to dict
            sessions = []
            count = 0;
            for i in range(len(sessions_arr)):
                #check if session is sceduled for adf
                if(datetime.now().date() < sessions_arr[i][2]) or ((datetime.now().date() == sessions_arr[i][2]) and (datetime.now().time() < sessions_arr[i][1])):
                    sessions.append({})
                    #TODO: Convert times here
                    sessions[count]['start_time'] = sessions_arr[i][0]
                    sessions[count]['end_time'] = sessions_arr[i][1]
                    sessions[count]['date'] = sessions_arr[i][2]
                    sessions[count]['building'] = sessions_arr[i][3]
                    sessions[count]['room_number'] = sessions_arr[i][4]
                    sessions[count]['description'] = sessions_arr[i][5]
                    sessions[count]['seshID'] = sessions_arr[i][6]
                    sessions[count]['class_code'] = sessions_arr[i][7]
                    sessions[count]['class_name'] = sessions_arr[i][8]
                    count+=1

            cursor.execute("SELECT      home_sessionhas.is_owner, \
                                        home_studysession.seshID \
                            FROM        accounts_enrolledin, \
                                        home_classes, \
                                        home_classofsession, \
                                        home_studysession, \
                                        home_sessionhas \
                            WHERE       accounts_enrolledin.netID = %s AND \
                                        home_sessionhas.netID = accounts_enrolledin.netID AND \
                                        accounts_enrolledin.class_code = home_classes.class_code AND \
                                        home_classes.class_code = home_classofsession.class_code AND \
                                        home_classofsession.seshID = home_studysession.seshID AND \
                                        home_classofsession.seshID = home_sessionhas.seshID", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)

            for i in range(len(sessions)):
                sessions[i]['is_owner'] = 0
                sessions[i]['is_joined'] = 0
            for i in range(len(sessions_arr)):
                for j in range(len(sessions)):
                    if(sessions[j]['seshID'] == sessions_arr[i][1]):
                        sessions[i]['is_owner'] = sessions_arr[i][0]
                        sessions[i]['is_joined'] = 1

            # find classes user is enrolled in and are empty
            cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                            FROM             accounts_enrolledin \
                            WHERE            %s = accounts_enrolledin.netID AND \
                                             accounts_enrolledin.class_code IN( \
                                                SELECT DISTINCT home_classofsession.class_code \
                                                FROM home_studysession, home_classofsession \
                                                WHERE home_studysession.seshID = home_classofsession.seshID)", [str(request.user)])

            #reorganize queryset to dict
            enrolledin_empty_arr = cursor.fetchall()
            enrolledin_empty = []
            for i in range(len(enrolledin_empty_arr)):
                enrolledin_empty.append(enrolledin_empty_arr[i][0])


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
                if(enrolledin[i]['class_code'] in enrolledin_empty):
                    enrolledin[i]['class_empty'] = False
                else:
                    enrolledin[i]['class_empty'] = True


            # find number of sessions joined by the user
            cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                            FROM             home_studysession, \
                                             home_sessionhas \
                            WHERE            %s = home_sessionhas.netID AND \
                                             home_studysession.seshID = home_sessionhas.seshID", [str(request.user)])

            #reorganize queryset to dict
            sessions_joined_arr = cursor.fetchall()
            sessions_joined = 0
            sessions_joined = sessions_joined_arr[0][0]

            # find number of sessions created by the user
            cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                            FROM             home_studysession, \
                                             home_sessionhas \
                            WHERE            %s = home_sessionhas.netID AND \
                                             home_studysession.seshID = home_sessionhas.seshID AND \
                                             home_sessionhas.is_owner = 1", [str(request.user)])

            #reorganize queryset to dict
            sessions_created_arr = cursor.fetchall()
            sessions_created = 0
            sessions_created = sessions_created_arr[0][0]

            connection.close()

            #print(sessions)
            args = {'sessions': sessions, 'enrolledin': enrolledin, 'sessions_joined': sessions_joined, 'sessions_created': sessions_created}
            #print(sessions)
            return render(request, self.template_name, args)

        elif function == "edit":

            return redirect(reverse('home:edit_session', kwargs={"seshID": seshID}))

        else:
            return HttpResponse("You shouldn't be here")





class NewSessionView(TemplateView):
    template_name = 'home/new_session.html'

    def get(self, request):
        cursor = connection.cursor()
        #find current enrolled classes
        cursor.execute("SELECT  accounts_enrolledin.class_code  \
                        FROM    accounts_enrolledin \
                        WHERE   accounts_enrolledin.netID = %s", [str(request.user)])
        middleman = cursor.fetchall()
        classes = []
        for i in range(len(middleman)):
            classes.append(middleman[i][0])
        class_dict = {}
        #need to obtain weights for every class scenario
        for curr_class in classes:
            #obtain all the users and corresponding dates that current user has studied
            cursor.execute("SELECT  s2.netID, home_studysession.date        \
                            FROM    home_sessionhas s1,               \
                                    home_sessionhas s2,               \
                                    home_classofsession,             \
                                    home_studysession           \
                            WHERE   %s = s1.netID AND \
                                    s1.seshID = home_classofsession.seshID  AND \
                                    s1.seshID = home_studysession.seshID    AND \
                                    home_classofsession.class_code = %s     AND \
                                    s1.netID <> s2.netID    AND \
                                    s1.seshID = s2.seshID", [str(request.user), str(curr_class)])

            date_arr = cursor.fetchall()
            #print(date_arr)
            exists_dict = {}
            session_arr = []
            for i in range(len(date_arr)):
                if date_arr[i][0] not in exists_dict:
                    if (datetime.now().date() - date_arr[i][1]).days >= 0:
                        exists_dict[date_arr[i][0]] = len(session_arr)
                        session_arr.append([])
                        session_arr[len(session_arr)-1].append(date_arr[i][0])
                        session_arr[len(session_arr)-1].append(1)
                        session_arr[len(session_arr)-1].append(date_arr[i][1])
                elif (datetime.now().date() - date_arr[i][1]).days >= 0 and (date_arr[i][1] - session_arr[exists_dict[date_arr[i][0]]][2]).days >= 0:
                        session_arr[exists_dict[date_arr[i][0]]][1] += 1
                        session_arr[exists_dict[date_arr[i][0]]][2] = date_arr[i][1]
            #print(session_arr)
            #aggregate the study sessions
            user_dict = {}
            #define weights
            for i in range(len(session_arr)):
                user_dict[session_arr[i][0]] = 4 + session_arr[i][1]
                #apply decay if in past
                delta = datetime.now().date() - session_arr[i][2]
                if delta.days >= 0:
                    user_dict[session_arr[i][0]] = max(0, user_dict[session_arr[i][0]] - (int(delta.days/14)))
            #print(user_dict)

            #MOM (Mate of a Mate) search. Go into current suggests and see if they have any strong relations
            mate_dict = []
            for j in user_dict.keys():
                mate_dict.append({})
                #go through each linked user and see who they have worked with and update the user dict
                cursor.execute("SELECT  s2.netID, home_studysession.date        \
                                FROM    home_sessionhas s1,               \
                                        home_sessionhas s2,               \
                                        home_classofsession,             \
                                        home_studysession           \
                                WHERE   %s = s1.netID AND \
                                        s1.seshID = home_classofsession.seshID  AND \
                                        s1.seshID = home_studysession.seshID    AND \
                                        home_classofsession.class_code = %s     AND \
                                        s1.netID <> s2.netID    AND \
                                        s2.netID <> %s  AND \
                                        s1.seshID = s2.seshID", [str(j), str(curr_class), str(request.user)])


                date_arr = cursor.fetchall()
                #print(date_arr)
                exists_dict = {}
                temp_arr = []
                for i in range(len(date_arr)):
                    if date_arr[i][0] not in exists_dict:
                        if (datetime.now().date() - date_arr[i][1]).days >= 0:
                            exists_dict[date_arr[i][0]] = len(temp_arr)
                            temp_arr.append([])
                            temp_arr[len(temp_arr)-1].append(date_arr[i][0])
                            temp_arr[len(temp_arr)-1].append(1)
                            temp_arr[len(temp_arr)-1].append(date_arr[i][1])
                    elif (datetime.now().date() - date_arr[i][1]).days >= 0 and (date_arr[i][1] - temp_arr[exists_dict[date_arr[i][0]]][2]).days >= 0:
                            temp_arr[exists_dict[date_arr[i][0]]][1] += 1
                            temp_arr[exists_dict[date_arr[i][0]]][2] = date_arr[i][1]

                #aggregate the study sessions
                for i in range(len(temp_arr)):
                    mate_dict[len(mate_dict)-1][temp_arr[i][0]] = 4 + temp_arr[i][1]
                    delta = datetime.now().date() - temp_arr[i][2]
                    if delta.days >= 0:
                        #initalize the dictionary
                        mate_dict[len(mate_dict)-1][temp_arr[i][0]] = int(max(0, mate_dict[len(mate_dict)-1][temp_arr[i][0]] - (int(delta.days/14))))


            for j in range(len(mate_dict)):
                #using the values in this dictionary, store into user dict
                for i in mate_dict[j].keys():
                    if i not in user_dict.keys():
                        user_dict[i] = int(float(mate_dict[j][i]*0.20) + 0.5)
                    else:
                        user_dict[i] = max(int(float(mate_dict[j][i]*0.20) + 0.5), user_dict[i])
            #sort user_dict
            #print(user_dict)
            sorted_x = sorted(user_dict.items(), key=operator.itemgetter(1), reverse = True)
            class_dict[curr_class] = sorted_x
            #print(sorted_x)

        #find top 5 per class
        for i in classes:
            temp_list = []
            count = 0
            for j in range(len(class_dict[i])):
                temp_list.append([])
                temp_list[j] = class_dict[i][j]
                count += 1
                if count >= 5:
                    break;
            class_dict[i] = temp_list

        #debug print
        # for j in class_dict.keys():
        #     print(j)
        #     for i in range(len(class_dict[j])):
        #         print(str(class_dict[j][i][1]) + " Weight for study mate " + str(class_dict[j][i][0]))

        #find all buildings on campus
        cursor.execute("SELECT      map_buildings.building  \
                        FROM        map_buildings \
                        ORDER BY    map_buildings.building")

        buildings_arr = cursor.fetchall()

        buildings = []
        for i in range(len(buildings_arr)):
            buildings.append(buildings_arr[i][0])

        cursor.close()

        form = NewSessionForm()

        # use this if jquery works
        #js_class_dict = json.dumps(class_dict)
        #print(type(js_class_dict))
        #print(class_dict)

        args = {'form': form, 'buildings': buildings, 'classes': classes, 'class_dict': class_dict}
        return render(request, self.template_name, args)

    def post(self, request):
        #temp_post = request.POST.copy() use this to edit the request.POST
        req = request.POST.copy()
        is_correct = True

        #check enrolled class TODO
        # check_class = re.compile('regex here')
        # if not check_class.match(req['enrolled_class']:
        #     is_correct = False

        #check start_time and end_time TODO
        # check_time = re.compile('regex here')
        # if not check_time.match(req['start_time']:
        #     is_correct = False
        # if not check_time.match(req['end_time']:
        #     is_correct = False

        #TODO:CHECK FOR LIMIT ON CREATION COUNT
        cursor = connection.cursor()

        #check for max seshes
        cursor.execute("SELECT COUNT    (DISTINCT home_studysession.seshID)  \
                        FROM            home_studysession, \
                                        home_sessionhas \
                        WHERE           home_studysession.seshID = home_sessionhas.seshID AND \
                                        home_sessionhas.is_owner = 1 AND \
                                        home_sessionhas.netID = %s", [str(request.user)])

        sesh_created_arr = cursor.fetchall()

        sesh_created = sesh_created_arr[0][0]

        cursor.close()

        if(sesh_created >= 5):
            #GET REQUEST
            # find session corresponding to users enrolled ClassOfSession
            cursor = connection.cursor()
            cursor.execute("SELECT      home_studysession.start_time, \
                                        home_studysession.end_time, \
                                        home_studysession.date, \
                                        home_studysession.building, \
                                        home_studysession.room_number, \
                                        home_studysession.description, \
                                        home_studysession.seshID, \
                                        home_classes.class_code, \
                                        home_classes.class_name \
                            FROM        accounts_enrolledin, \
                                        home_classes, \
                                        home_classofsession, \
                                        home_studysession \
                            WHERE       accounts_enrolledin.netID = %s AND \
                                        accounts_enrolledin.class_code = home_classes.class_code AND \
                                        home_classes.class_code = home_classofsession.class_code AND \
                                        home_classofsession.seshID = home_studysession.seshID \
                            ORDER BY    datetime(home_studysession.date), \
                                        datetime(home_studysession.start_time), \
                                        datetime(home_studysession.end_time), \
                                        home_studysession.building, \
                                        home_studysession.room_number", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)
            #reorganize queryset to dict
            sessions = []
            count = 0;
            for i in range(len(sessions_arr)):
                #check if session is sceduled for adf
                if(datetime.now().date() < sessions_arr[i][2]) or ((datetime.now().date() == sessions_arr[i][2]) and (datetime.now().time() < sessions_arr[i][1])):
                    sessions.append({})
                    sessions[count]['start_time'] = sessions_arr[i][0]
                    sessions[count]['end_time'] = sessions_arr[i][1]
                    sessions[count]['date'] = sessions_arr[i][2]
                    sessions[count]['building'] = sessions_arr[i][3]
                    sessions[count]['room_number'] = sessions_arr[i][4]
                    sessions[count]['description'] = sessions_arr[i][5]
                    sessions[count]['seshID'] = sessions_arr[i][6]
                    sessions[count]['class_code'] = sessions_arr[i][7]
                    sessions[count]['class_name'] = sessions_arr[i][8]
                    count+=1

            cursor.execute("SELECT      home_sessionhas.is_owner, \
                                        home_studysession.seshID \
                            FROM        accounts_enrolledin, \
                                        home_classes, \
                                        home_classofsession, \
                                        home_studysession, \
                                        home_sessionhas \
                            WHERE       accounts_enrolledin.netID = %s AND \
                                        home_sessionhas.netID = accounts_enrolledin.netID AND \
                                        accounts_enrolledin.class_code = home_classes.class_code AND \
                                        home_classes.class_code = home_classofsession.class_code AND \
                                        home_classofsession.seshID = home_studysession.seshID AND \
                                        home_classofsession.seshID = home_sessionhas.seshID", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)

            for i in range(len(sessions)):
                sessions[i]['is_owner'] = 0
                sessions[i]['is_joined'] = 0
            for i in range(len(sessions_arr)):
                for j in range(len(sessions)):
                    if(sessions[j]['seshID'] == sessions_arr[i][1]):
                        sessions[j]['is_owner'] = sessions_arr[i][0]
                        sessions[j]['is_joined'] = 1

            # find classes user is enrolled in and are empty
            cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                            FROM             accounts_enrolledin \
                            WHERE            %s = accounts_enrolledin.netID AND \
                                             accounts_enrolledin.class_code IN( \
                                                SELECT DISTINCT home_classofsession.class_code \
                                                FROM home_studysession, home_classofsession \
                                                WHERE home_studysession.seshID = home_classofsession.seshID)", [str(request.user)])

            #reorganize queryset to dict
            enrolledin_empty_arr = cursor.fetchall()
            enrolledin_empty = []
            for i in range(len(enrolledin_empty_arr)):
                enrolledin_empty.append(enrolledin_empty_arr[i][0])


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
                if(enrolledin[i]['class_code'] in enrolledin_empty):
                    enrolledin[i]['class_empty'] = False
                else:
                    enrolledin[i]['class_empty'] = True


            # find number of sessions joined by the user
            cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                            FROM             home_studysession, \
                                             home_sessionhas \
                            WHERE            %s = home_sessionhas.netID AND \
                                             home_studysession.seshID = home_sessionhas.seshID", [str(request.user)])

            #reorganize queryset to dict
            sessions_joined_arr = cursor.fetchall()
            sessions_joined = 0
            sessions_joined = sessions_joined_arr[0][0]

            # find number of sessions created by the user
            cursor.execute("SELECT COUNT     (DISTINCT home_studysession.seshID) \
                            FROM             home_studysession, \
                                             home_sessionhas \
                            WHERE            %s = home_sessionhas.netID AND \
                                             home_studysession.seshID = home_sessionhas.seshID AND \
                                             %s = home_sessionhas.is_owner", [str(request.user), True])

            #reorganize queryset to dict
            sessions_created_arr = cursor.fetchall()
            sessions_created = 0
            sessions_created = sessions_created_arr[0][0]

            cursor.close()

            #print(sessions)
            args = {'sessions': sessions, 'enrolledin': enrolledin, 'sessions_joined': sessions_joined, 'sessions_created': sessions_created}
            #print(sessions)
            return render(request, "home/homepage.html", args)

        cursor.close()


        #Change html input to django inputs TODO: REGEX STUFF HERE

        #start time
        colon_idx = -1
        am_or_pm = ""

        for i in range(0, len(req['start_time'])):
            if(req['start_time'][i] == ':'):
                colon_idx = i;
            elif(colon_idx != -1 and req['start_time'][i] == 'a'):
                am_or_pm = "am"
                break
            elif(colon_idx != -1 and req['start_time'][i] == 'p'):
                am_or_pm = "pm"
                break


        start_min_str = req['start_time'][colon_idx + 1:colon_idx + 3]
        start_min = int(req['start_time'][colon_idx + 1:colon_idx + 3])

        start_hours_str = req['start_time'][:colon_idx]
        start_hours = int(req['start_time'][:colon_idx])

        #HH pm = HH+12
        if (am_or_pm == "pm" and start_hours != 12):
            start_hours = start_hours + 12
            start_hours_str = str(start_hours)
        #12am = 00
        elif (am_or_pm == "am" and start_hours == 12):
            start_hours_str = "0"
            start_hours = 0

        #changes H to HH
        if(len(start_hours_str) == 1):
            start_hours_str = "0" + start_hours_str

        req['start_time'] = start_hours_str + ':' + start_min_str


        #end time
        colon_idx = -1
        am_or_pm = ""

        for i in range(0, len(req['end_time'])):
            if(req['end_time'][i] == ':'):
                colon_idx = i;
            elif(colon_idx != -1 and req['end_time'][i] == 'a'):
                am_or_pm = "am"
                break
            elif(colon_idx != -1 and req['end_time'][i] == 'p'):
                am_or_pm = "pm"
                break


        end_min_str = req['end_time'][colon_idx + 1:colon_idx + 3]
        end_min = int(req['end_time'][colon_idx + 1:colon_idx + 3])

        end_hours_str = req['end_time'][:colon_idx]
        end_hours = int(req['end_time'][:colon_idx])

        #HH pm = HH+12
        if (am_or_pm == "pm" and end_hours != 12):
            end_hours = end_hours + 12
            end_hours_str = str(end_hours)
        #12am = 00
        elif (am_or_pm == "am" and end_hours == 12):
            end_hours_str = "0"
            end_hours = 0

        #changes H to HH
        if(len(end_hours_str) == 1):
            end_hours_str = "0" + end_hours_str

        req['end_time'] = end_hours_str + ':' + end_min_str

        #print("start_hours" + str(start_hours))
        #print("start_min" + str(start_min))
        #print("end_hours" + str(end_hours))
        #print("end_min" + str(end_min))

        #check for valid bounds here
        if(end_hours == start_hours):
            if(end_min <= start_min):
                is_correct = False
        elif(end_hours < start_hours):
            is_correct = False


        #check date TODO REGEX
        # check_date = re.compile('regex here')
        # if not check_date.match(req['date']:
        #     is_correct = False

        #fix date here
        first_slash_idx = -1
        second_slash_idx = -1
        for i in range(0, len(req['date'])):
            if(req['date'][i] == '/'):
                if(first_slash_idx == -1):
                    first_slash_idx = i
                else:
                    second_slash_idx = i
                    break

        req['date'] = req['date'][second_slash_idx+1:] + '-' + req['date'][:first_slash_idx] + '-' + req['date'][first_slash_idx+1:second_slash_idx]


        #check building TODO REGEX
        # check_building = re.compile('regex here')
        # if not check_building.match(req['building']:
        #     is_correct = False

        #check room_number TODO REGEX
        # check_room = re.compile('regex here')
        # if not check_room.match(req['date']:
        #     is_correct = False

        #check invited_friends (not done atm)

        #use regex to determine true of false here
        #STILL NEED TO CHECK IF THE USER OWNS THE STUDY SESSION THEY ARE EDITING

        #temp = re.compile("regex here")
        #temp.match("input string")
        #need to fix data here


        if not is_correct:
            return redirect(reverse('home:new_session'))

        form = NewSessionForm(req)

        #example post request below:
        # <QueryDict: {
        # 'csrfmiddlewaretoken': ['nc8vJkznn8z1ZJeFwe4xdokfEg7lx7grKiIyNGwujoS0f0n6xRiUhM80HtQUlotB'],
        # 'enrolled_class': ['CS411'], 'start_time': ['12:30am'], 'end_time': ['1:30am'],
        # 'date': ['04/18/2018'], 'building': ['ECEB'], 'room_number': ['1000'],
        # 'description': ['asdasdasdadasdad'], 'invited_friends': ['bill', 'joe']}>

        if form.is_valid(): #override is_valid later for more restriction
            #sql query here
            form.save(request);
            # StudySession.objects.raw('INSERT INTO  home_studysession(start_time,
            #                                        end_time,
            #                                        date,
            #                                        building,
            #                                        room_number,
            #                                        description) \
            #                           VALUES       auth_user, \
            #                                        accounts_enrolledin, \
            #                                        home_classes')

            return redirect(reverse('home:home'))
        else:
            return redirect(reverse('home:new_session')) #deal with fail cases here


class EditSessionView(TemplateView):
    template_name = 'home/edit_session.html'

    def get(self, request, seshID):
        form = EditSessionForm(seshID)
        #print(form.fields["enrolled_class"].to_python('s'))
        cursor = connection.cursor()
        #find current enrolled classes
        cursor.execute("SELECT  accounts_enrolledin.class_code  \
                        FROM    accounts_enrolledin \
                        WHERE   accounts_enrolledin.netID = %s", [str(request.user)])
        classes_arr = cursor.fetchall()
        classes = []
        for i in range(len(classes_arr)):
            classes.append(classes_arr[i][0])

        cursor.execute("SELECT      home_studysession.start_time, \
                                    home_studysession.end_time, \
                                    home_studysession.date, \
                                    home_studysession.building, \
                                    home_studysession.room_number, \
                                    home_studysession.description, \
                                    home_classofsession.class_code \
                        FROM        home_classofsession, \
                                    home_studysession \
                        WHERE       home_classofsession.seshID = %s AND \
                                    home_studysession.seshID = %s", [seshID, seshID])

        old_session_sql = cursor.fetchall()


        old_session_data = {}
        old_session_data["start_time"] = old_session_sql[0][0]
        old_session_data["end_time"] = old_session_sql[0][1]
        old_session_data["date"] = str(old_session_sql[0][2])[5:7] + "/" + str(old_session_sql[0][2])[8:10] + "/" + str(old_session_sql[0][2])[:4]
        old_session_data["building"] = old_session_sql[0][3]
        old_session_data["room_number"] = old_session_sql[0][4]
        old_session_data["description"] = old_session_sql[0][5]
        old_session_data["enrolled_class"] = old_session_sql[0][6]

        #TODO: Convert times to proper strings here
        #print(old_session_data["start_time"].hour)
        am_or_pm = ""
        start_hrs = int(old_session_data["start_time"].hour)
        if(start_hrs < 12):
            if(start_hrs == 0):
                start_hrs = 12
            start_hrs_str = str(start_hrs)
            am_or_pm = "am"
        else:
            if(start_hrs != 12):
                start_hrs -= 12
            start_hrs_str = str(start_hrs)
            am_or_pm = "pm"

        start_mins_str = str(old_session_data["start_time"].minute)
        if(len(start_mins_str) == 1):
            start_mins_str = "0" + start_mins_str

        old_session_data["start_time"] = start_hrs_str + ":" + start_mins_str + am_or_pm
        #print(old_session_data["start_time"])

        am_or_pm = ""
        end_hrs = int(old_session_data["end_time"].hour)
        if(end_hrs < 12):
            if(end_hrs == 0):
                end_hrs = 12
            end_hrs_str = str(end_hrs)
            am_or_pm = "am"
        else:
            if(end_hrs != 12):
                end_hrs -= 12
            end_hrs_str = str(end_hrs)
            am_or_pm = "pm"

        end_mins_str = str(old_session_data["end_time"].minute)
        if(len(end_mins_str) == 1):
            end_mins_str = "0" + end_mins_str

        old_session_data["end_time"] = end_hrs_str + ":" + end_mins_str + am_or_pm

        #find all buildings on campus
        cursor.execute("SELECT      map_buildings.building  \
                        FROM        map_buildings \
                        ORDER BY    map_buildings.building")

        buildings_arr = cursor.fetchall()

        buildings = []
        for i in range(len(buildings_arr)):
            buildings.append(buildings_arr[i][0])

        cursor.close()

        print(old_session_data)
        args = {'form': form, 'buildings': buildings, 'classes': classes, 'old_session_data': old_session_data}
        return render(request, self.template_name, args)

    def post(self, request, seshID):
        form = EditSessionForm(seshID)

        req = request.POST.copy()
        is_correct = True

        #check enrolled class
        # check_class = re.compile('regex here')
        # if not check_class.match(req['enrolled_class']:
        #     is_correct = False

        #check start_time and end_time
        # check_time = re.compile('regex here')
        # if not check_time.match(req['start_time']:
        #     is_correct = False
        # if not check_time.match(req['end_time']:
        #     is_correct = False


        #Change html input to django inputs TODO: REGEX STUFF HERE

        #start time
        colon_idx = -1
        am_or_pm = ""

        for i in range(0, len(req['start_time'])):
            if(req['start_time'][i] == ':'):
                colon_idx = i;
            elif(colon_idx != -1 and req['start_time'][i] == 'a'):
                am_or_pm = "am"
                break
            elif(colon_idx != -1 and req['start_time'][i] == 'p'):
                am_or_pm = "pm"
                break


        start_min_str = req['start_time'][colon_idx + 1:colon_idx + 3]
        start_min = int(req['start_time'][colon_idx + 1:colon_idx + 3])

        start_hours_str = req['start_time'][:colon_idx]
        start_hours = int(req['start_time'][:colon_idx])

        #HH pm = HH+12
        if (am_or_pm == "pm" and start_hours != 12):
            start_hours = start_hours + 12
            start_hours_str = str(start_hours)
        #12am = 00
        elif (am_or_pm == "am" and start_hours == 12):
            start_hours_str = "0"
            start_hours = 0

        #changes H to HH
        if(len(start_hours_str) == 1):
            start_hours_str = "0" + start_hours_str

        req['start_time'] = start_hours_str + ':' + start_min_str


        #end time
        colon_idx = -1
        am_or_pm = ""

        for i in range(0, len(req['end_time'])):
            if(req['end_time'][i] == ':'):
                colon_idx = i;
            elif(colon_idx != -1 and req['end_time'][i] == 'a'):
                am_or_pm = "am"
                break
            elif(colon_idx != -1 and req['end_time'][i] == 'p'):
                am_or_pm = "pm"
                break


        end_min_str = req['end_time'][colon_idx + 1:colon_idx + 3]
        end_min = int(req['end_time'][colon_idx + 1:colon_idx + 3])

        end_hours_str = req['end_time'][:colon_idx]
        end_hours = int(req['end_time'][:colon_idx])

        #HH pm = HH+12
        if (am_or_pm == "pm" and end_hours != 12):
            end_hours = end_hours + 12
            end_hours_str = str(end_hours)
        #12am = 00
        elif (am_or_pm == "am" and end_hours == 12):
            end_hours_str = "0"
            end_hours = 0

        #changes H to HH
        if(len(end_hours_str) == 1):
            end_hours_str = "0" + end_hours_str

        req['end_time'] = end_hours_str + ':' + end_min_str

        #print("start_hours" + start_hours)
        #print("start_min" + start_min)
        #print("end_hours" + end_hours)
        #print("end_min" + end_min)

        #check for valid bounds here
        if(end_hours == start_hours):
            if(end_min <= start_min):
                is_correct = False
        elif(end_hours < start_hours):
            is_correct = False


        #check date TODO REGEX
        # check_date = re.compile('regex here')
        # if not check_date.match(req['date']:
        #     is_correct = False

        #fix date here
        first_slash_idx = -1
        second_slash_idx = -1
        for i in range(0, len(req['date'])):
            if(req['date'][i] == '/'):
                if(first_slash_idx == -1):
                    first_slash_idx = i
                else:
                    second_slash_idx = i
                    break

        req['date'] = req['date'][second_slash_idx+1:] + '-' + req['date'][:first_slash_idx] + '-' + req['date'][first_slash_idx+1:second_slash_idx]


        #check building TODO REGEX
        # check_building = re.compile('regex here')
        # if not check_building.match(req['building']:
        #     is_correct = False

        #check room_number TODO REGEX
        # check_room = re.compile('regex here')
        # if not check_room.match(req['date']:
        #     is_correct = False

        #check invited_friends (not done atm)

        #use regex to determine true of false here
        #STILL NEED TO CHECK IF THE USER OWNS THE STUDY SESSION THEY ARE EDITING

        #temp = re.compile("regex here")
        #temp.match("input string")
        #need to fix data here


        if not is_correct:
            return redirect(reverse('home:edit_session', kwargs={"seshID": seshID}))

        if form.is_valid(): #override is_valid later for more restriction
            #sql query here
            #print(request)

            form.save(req, seshID);
            # StudySession.objects.raw('INSERT INTO  home_studysession(start_time,
            #                                        end_time,
            #                                        date,
            #                                        building,
            #                                        room_number,
            #                                        description) \
            #                           VALUES       auth_user, \
            #                                        accounts_enrolledin, \
            #                                        home_classes')

            return redirect(reverse('home:home'))
        else:
            return redirect(reverse('home:edit_session'), ) #deal with fail cases here
