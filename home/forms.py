import uuid
from django import forms
from django.db import connection #sql

class NewSessionForm(forms.Form):
    enrolled_class = forms.CharField(required=True, label="Class", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ECE313...' }))
    start_time = forms.CharField(required=True, label="Start Time", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM...' }))
    end_time = forms.CharField(required=True, label="End Time", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM...' }))
    date = forms.DateField(required=True, label="Date", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD...' }))
    building = forms.CharField(required=True, label="Building", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text...' }))
    room_number = forms.CharField(required=True, label="Room Number", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '101...' }))
    description = forms.CharField(required=False, label="Description", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text...' }))

    #populate an array for sesh relations
    cursor = connection.cursor()

    #obtain array of every other user that has been in a sessino with the current user

    cursor.execute("SELECT  s2.netID, COUNT(s2.seshID)        \
                    FROM    home_sessionhas s1,               \
                            home_sessionhas s2,               \
                            auth_user \
                    WHERE   auth_user.username = s1.netID AND \
                            s1.seshID = s2.seshID  ")

    session_arr = cursor.fetchall()
    print(session_arr)


    cursor.close()
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
