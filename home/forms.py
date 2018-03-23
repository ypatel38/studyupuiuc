import uuid
from django import forms
from django.db import connection #sql

class NewSessionForm(forms.Form):
    enrolled_class = forms.CharField(required=True, label="Class")
    start_time = forms.CharField(required=True, label="Start Time")
    end_time = forms.CharField(required=True, label="Last Name")
    date = forms.DateField(required=True, label="Date")
    building = forms.CharField(required=True, label="Building")
    room_number = forms.CharField(required=True, label="Room Number")
    description = forms.CharField(required=False, label="Description")

    def is_valid(self):
        #use regex to determine true of false here
        return True

    def save(self, request):

                session_data = {}

                for each in self:
                    id = each.auto_id
                    value = each.value()
                    session_data[id] = value

                new_session_id = str(uuid.uuid4()) #note in postrgress this might not want to be str

                cursor = connection.cursor()

                #add new session in sql
                cursor.execute("INSERT INTO  home_studysession(start_time, \
                                                               end_time, \
                                                               date, \
                                                               building, \
                                                               room_number, \
                                                               description, \
                                                               seshID) \
                                VALUES       (%s, \
                                              %s, \
                                              %s, \
                                              %s, \
                                              %s, \
                                              %s, \
                                              %s)",
                                              [session_data['id_' + 'start_time'],
                                              session_data['id_' + 'end_time'],
                                              session_data['id_' + 'date'],
                                              session_data['id_' + 'building'],
                                              session_data['id_' + 'room_number'],
                                              session_data['id_' + 'description'],
                                              new_session_id])

                #add class of session in sql
                cursor.execute("INSERT INTO  home_classofsession(class_code, \
                                                                 seshID) \
                                VALUES       (%s, \
                                              %s)",
                                              [session_data['id_' + 'enrolled_class'],
                                              new_session_id])

                #add host as member of the session
                cursor.execute("INSERT INTO  home_sessionhas(netID, \
                                                             seshID, \
                                                             is_owner) \
                                VALUES       (%s, \
                                              %s, \
                                              %s)",
                                              [request.user.username,
                                              new_session_id,
                                              True])
