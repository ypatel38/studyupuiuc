from django.views.generic import TemplateView
from django.shortcuts import render
from django.db import connection #sql

# Create your views here.

class HomeView(TemplateView):
    template_name = "home/homepage.html"

    def get(self, request):
        #sql query's here to get all info and put into args (temp)
        #TODO: THIS QUERY IS TEMPORARY FOR A TEST, NEEDS TO BE CLEANED UP WITH SORTS, ORGANIZED ARGS, ETC!!!

        cursor = connection.cursor()
        cursor.execute("SELECT      home_studysession.start_time, \
                                    home_studysession.end_time, \
                                    home_studysession.date, \
                                    home_studysession.building, \
                                    home_studysession.room_number, \
                                    home_studysession.description, \
                                    home_classes.class_code, \
                                    home_classes.class_name \
                        FROM        auth_user, \
                                    accounts_enrolledin, \
                                    home_classes, \
                                    home_classofsession, \
                                    home_studysession \
                        WHERE       auth_user.username = accounts_enrolledin.netID AND \
                                    accounts_enrolledin.class_code = home_classes.class_code AND \
                                    home_classes.class_code = home_classofsession.class_code AND \
                                    home_classofsession.seshID = home_studysession.seshID \
                        ORDER BY    home_studysession.start_time")
                        
        sessions = cursor.fetchall()

        cursor.execute("SELECT DISTINCT  accounts_enrolledin.class_code \
                        FROM             auth_user, \
                                         accounts_enrolledin, \
                                         home_classes \
                        WHERE            auth_user.username = accounts_enrolledin.netID")

        enrolledin = cursor.fetchall()

        connection.close()

        print(enrolledin)
        args = {'sessions': sessions, 'enrolledin': enrolledin}
        return render(request, self.template_name, args)

    def post(self, request):
        pass
