from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.db import connection #sql
from django.urls import reverse #used for namespaces
from django.http import HttpResponse
from home.forms import *
from datetime import datetime, timedelta

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
                        ORDER BY    home_studysession.start_time", [str(request.user)])

        sessions_arr = cursor.fetchall()
        #print(sessions_arr)
        #reorganize queryset to dict
        sessions = []
        for i in range(len(sessions_arr)):
            sessions.append({})
            sessions[i]['start_time'] = sessions_arr[i][0]
            sessions[i]['end_time'] = sessions_arr[i][1]
            sessions[i]['date'] = sessions_arr[i][2]
            sessions[i]['building'] = sessions_arr[i][3]
            sessions[i]['room_number'] = sessions_arr[i][4]
            sessions[i]['description'] = sessions_arr[i][5]
            sessions[i]['seshID'] = sessions_arr[i][6]
            sessions[i]['class_code'] = sessions_arr[i][7]
            sessions[i]['class_name'] = sessions_arr[i][8]

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
                                    home_classofsession.seshID = home_sessionhas.seshID \
                        ORDER BY    home_studysession.start_time", [str(request.user)])

        sessions_arr = cursor.fetchall()
        print(sessions_arr)

        for i in range(len(sessions)):
            sessions[i]['is_owner'] = 0
            sessions[i]['is_joined'] = 0
        for i in range(len(sessions_arr)):
            for j in range(len(sessions)):
                if(sessions[j]['seshID'] == sessions_arr[i][1]):
                    sessions[j]['is_owner'] = sessions_arr[i][0]
                    sessions[j]['is_joined'] = 1

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
            enrolledin[i]['auth_user'] = enrolledin_arr[i][0]

        connection.close()
        #print(sessions)
        args = {'sessions': sessions, 'enrolledin': enrolledin}
        #print(sessions)
        return render(request, self.template_name, args)


    def post(self, request):
        print("HELLO")
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
    
            print(is_joined)
            print(seshID)
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
                            ORDER BY    home_studysession.start_time", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)
            #reorganize queryset to dict
            sessions = []
            for i in range(len(sessions_arr)):
                sessions.append({})
                sessions[i]['start_time'] = sessions_arr[i][0]
                sessions[i]['end_time'] = sessions_arr[i][1]
                sessions[i]['date'] = sessions_arr[i][2]
                sessions[i]['building'] = sessions_arr[i][3]
                sessions[i]['room_number'] = sessions_arr[i][4]
                sessions[i]['description'] = sessions_arr[i][5]
                sessions[i]['seshID'] = sessions_arr[i][6]
                sessions[i]['class_code'] = sessions_arr[i][7]
                sessions[i]['class_name'] = sessions_arr[i][8]

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
                                        home_classofsession.seshID = home_sessionhas.seshID \
                            ORDER BY    home_studysession.start_time", [str(request.user)])

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
                enrolledin[i]['auth_user'] = enrolledin_arr[i][0]

            connection.close()
            #print(sessions)
            args = {'sessions': sessions, 'enrolledin': enrolledin}
            print(sessions)
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
                            ORDER BY    home_studysession.start_time", [str(request.user)])

            sessions_arr = cursor.fetchall()
            #print(sessions_arr)
            #reorganize queryset to dict
            sessions = []
            for i in range(len(sessions_arr)):
                sessions.append({})
                sessions[i]['start_time'] = sessions_arr[i][0]
                sessions[i]['end_time'] = sessions_arr[i][1]
                sessions[i]['date'] = sessions_arr[i][2]
                sessions[i]['building'] = sessions_arr[i][3]
                sessions[i]['room_number'] = sessions_arr[i][4]
                sessions[i]['description'] = sessions_arr[i][5]
                sessions[i]['seshID'] = sessions_arr[i][6]
                sessions[i]['class_code'] = sessions_arr[i][7]
                sessions[i]['class_name'] = sessions_arr[i][8]

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
                                        home_classofsession.seshID = home_sessionhas.seshID \
                            ORDER BY    home_studysession.start_time", [str(request.user)])

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
                enrolledin[i]['auth_user'] = enrolledin_arr[i][0]

            connection.close()
            #print(sessions)
            args = {'sessions': sessions, 'enrolledin': enrolledin}
            print(sessions)
            return render(request, self.template_name, args)

        elif function == "edit":

            return redirect(reverse('home:edit_session', kwargs={"seshID": seshID}))

        else:
            return HttpResponse("ERROR")





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
            print(date_arr)
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
                        print(session_arr[exists_dict[date_arr[i][0]]][2])
                else:
                    session_arr[exists_dict[date_arr[i][0]]][1] += 1
                    if (datetime.now().date() - date_arr[i][1]).days >= 0 and (date_arr[i][1] - session_arr[exists_dict[date_arr[i][0]]][2]).days >= 0:
                        session_arr[exists_dict[date_arr[i][0]]][2] = date_arr[i][1]


            print(session_arr)
            #aggregate the study sessions
            user_dict = {}
            #define weights
            for i in range(len(session_arr)):
                user_dict[session_arr[i][0]] = 4 + session_arr[i][1]
                #apply decay if in past
                delta = datetime.now().date() - session_arr[i][2]
                if delta.days >= 0:
                    user_dict[session_arr[i][0]] = max(0, user_dict[session_arr[i][0]] - (int(delta.days/14)))
            print(user_dict)
            
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
                print(date_arr)
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
                            print(temp_arr[exists_dict[date_arr[i][0]]][2])
                    else:
                        temp_arr[exists_dict[date_arr[i][0]]][1] += 1
                        if (datetime.now().date() - date_arr[i][1]).days >= 0 and (date_arr[i][1] - temp_arr[exists_dict[date_arr[i][0]]][2]).days >= 0:
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

            class_dict[curr_class] = user_dict

        #debug print
        for j in class_dict.keys():
            print(j)
            for i in class_dict[j].keys():
                print(str(class_dict[j][i]) + " Weight for study mate " + str(i))
        
        cursor.close()

        form = NewSessionForm()
        args = {'form': form, 'class_dict': class_dict}
        return render(request, self.template_name, args)

    def post(self, request):
        form = NewSessionForm(request.POST)
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
        args = {'form': form}
        return render(request, self.template_name, args)

    def post(self, request, seshID):
        form = EditSessionForm(seshID)

        if form.is_valid(): #override is_valid later for more restriction
            #sql query here
            #print(request)

            form.save(request, seshID);
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
