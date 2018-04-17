from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.db import connection #sql
from django.urls import reverse #used for namespaces
from django.http import HttpResponse

from accounts.forms import RegistrationForm
from datetime import datetime



# Create your views here.
class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

    def get(self, request):
        form = RegistrationForm()
        args = {'form': form}
        print(form)
        return render(request, self.template_name, args)

    def post(self, request):
        form = RegistrationForm(request.POST)

        if form.is_valid(): #override is_valid later for more restriction
            form.save()
            return redirect(reverse('accounts:login'))
        else:
            return redirect(reverse('accounts:register')) #deal with fail cases here

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get(self, request):
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT     home_classes.class_code \
                        FROM                accounts_enrolledin, \
                                            home_classes \
                        WHERE               home_classes.class_code = accounts_enrolledin.class_code AND \
                                            accounts_enrolledin.netID = %s \
                        ORDER BY            home_classes.class_code", [str(request.user)])

        enrolled_classes_arr = cursor.fetchall()

        enrolled_classes = []

        for i in range(0, len(enrolled_classes_arr)):
            enrolled_classes.append(enrolled_classes_arr[i][0])

        #print(enrolled_classes)

        cursor = connection.cursor()

        # cursor.execute("SELECT DISTINCT     accounts_enrolledin.class_code \
        #                 FROM                accounts_enrolledin \
        #                 WHERE               accounts_enrolledin.netID = %s \
        #                 ORDER BY            accounts_enrolledin.class_code", [str(request.user)])
        # print(cursor.fetchall())
        # cursor.execute("SELECT DISTINCT     home_classes.class_code \
        #                 FROM                home_classes \
        #                 ORDER BY            home_classes.class_code")
        #
        #
        # print(cursor.fetchall())

        cursor.execute("SELECT DISTINCT     home_classes.class_code \
                        FROM                home_classes \
                        WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                        ORDER BY            home_classes.class_code", [str(request.user)])

        other_classses_arr = cursor.fetchall()

        other_classes = []

        for i in range(len(other_classses_arr)):
            other_classes.append(other_classses_arr[i][0])

        #print(other_classes)



        #########################################################################################################
        #       Snippet of code that obtains each location and the # of times it is actively being used         #
        #                       will be pasted in corresponding HTML page when it is created                    #
        #########################################################################################################

        cursor.execute("SELECT home_studysession.building, home_studysession.date, home_studysession.start_time, home_studysession.end_time, home_studysession.seshID        \
                        FROM home_studysession")
        building_arr = cursor.fetchall()

        #now that we have every study_session ever, i need to populate the return dictionary

        building_dict = {}
        today = datetime.now().date()
        valid_sesh = []
        curr_time = datetime.now()
        for i in range(len(building_arr)):
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


        print("Currently active study sessions: ")
        for i in building_dict.keys():
            print("There are", building_dict[i]['num_sesh'], "study sessions in", i, "with", building_dict[i]['num_students'], "students.")


        args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
        return render(request, self.template_name, args)

    def post(self, request):
        print(request.POST)
        #classes_select has added classes
        #remove_class has removed classes

        if("classes_select" in request.POST):
            function = "classes_select"
        elif("remove_class" in request.POST):
            function = "remove_class"
        else:
            function = "error"

        if function == "classes_select":
            #add classes to db here

            cursor = connection.cursor()

            joined_classes = request.POST.getlist('classes_select')

            for i in range(0, len(joined_classes)):
                cursor.execute("INSERT INTO     accounts_enrolledin(netID, class_code) \
                                VALUES          (%s, %s)", [str(request.user), joined_classes[i]])




            #get request
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT     home_classes.class_code \
                            FROM                accounts_enrolledin, \
                                                home_classes \
                            WHERE               home_classes.class_code = accounts_enrolledin.class_code AND \
                                                accounts_enrolledin.netID = %s \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            enrolled_classes_arr = cursor.fetchall()

            enrolled_classes = []

            for i in range(0, len(enrolled_classes_arr)):
                enrolled_classes.append(enrolled_classes_arr[i][0])

            #print(enrolled_classes)

            cursor = connection.cursor()

            cursor.execute("SELECT DISTINCT     home_classes.class_code \
                            FROM                home_classes \
                            WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            other_classses_arr = cursor.fetchall()

            other_classes = []

            for i in range(0, len(other_classses_arr)):
                other_classes.append(other_classses_arr[i][0])

            #print(other_classes)
            cursor.close()

            args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
            return render(request, self.template_name, args)

        elif function == "remove_class":
            #remove classes from db here

            cursor = connection.cursor()

            removed_class = request.POST['remove_class']


            cursor.execute("DELETE FROM     accounts_enrolledin \
                            WHERE           accounts_enrolledin.netID = %s AND \
                                            accounts_enrolledin.class_code = %s", [str(request.user), removed_class])



            #get request
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT     home_classes.class_code \
                            FROM                accounts_enrolledin, \
                                                home_classes \
                            WHERE               home_classes.class_code = accounts_enrolledin.class_code AND \
                                                accounts_enrolledin.netID = %s \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            enrolled_classes_arr = cursor.fetchall()

            enrolled_classes = []

            for i in range(0, len(enrolled_classes_arr)):
                enrolled_classes.append(enrolled_classes_arr[i][0])

            #print(enrolled_classes)

            cursor = connection.cursor()

            cursor.execute("SELECT DISTINCT     home_classes.class_code \
                            FROM                home_classes \
                            WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            other_classses_arr = cursor.fetchall()

            other_classes = []

            for i in range(0, len(other_classses_arr)):
                other_classes.append(other_classses_arr[i][0])

            #print(other_classes)
            cursor.close()

            args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
            return render(request, self.template_name, args)

        else:
            #get request
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT     home_classes.class_code \
                            FROM                accounts_enrolledin, \
                                                home_classes \
                            WHERE               home_classes.class_code = accounts_enrolledin.class_code AND \
                                                accounts_enrolledin.netID = %s \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            enrolled_classes_arr = cursor.fetchall()

            enrolled_classes = []

            for i in range(0, len(enrolled_classes_arr)):
                enrolled_classes.append(enrolled_classes_arr[i][0])

            #print(enrolled_classes)

            cursor = connection.cursor()

            cursor.execute("SELECT DISTINCT     home_classes.class_code \
                            FROM                home_classes \
                            WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            other_classses_arr = cursor.fetchall()

            other_classes = []

            for i in range(0, len(other_classses_arr)):
                other_classes.append(other_classses_arr[i][0])

            #print(other_classes)
            cursor.close()

            args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
            return render(request, self.template_name, args)
