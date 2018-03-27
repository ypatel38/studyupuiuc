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



    class Meta:
        fields = { #use if u want to whitelist
            'enrolled_class',
            'start_time',
            'end_time',
            'date',
            'building',
            'room_number',
            'description'
        }

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

class EditSessionForm(forms.Form):

    enrolled_class = forms.CharField(required=True, label="Class", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ECE313...' }))
    start_time = forms.CharField(required=True, label="Start Time", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM...' }))
    end_time = forms.CharField(required=True, label="End Time", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM...' }))
    date = forms.DateField(required=True, label="Date", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD...' }))
    building = forms.CharField(required=True, label="Building", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text...' }))
    room_number = forms.CharField(required=True, label="Room Number", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '101...' }))
    description = forms.CharField(required=False, label="Description", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text...' }))


    class Meta:
        fields = { #use if u want to whitelist
            'enrolled_class',
            'start_time',
            'end_time',
            'date',
            'building',
            'room_number',
            'description'
        }

    # def __init__(self, seshID, *args, **kwargs):
    #     super(EditSessionForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        #use regex to determine true of false here
        #STILL NEED TO CHECK IF THE USER OWNS THE STUDY SESSION THEY ARE EDITING
        return True

    def save(self, request, seshID):
        pass
        session_data = {}

        for each in self:
            id = each.auto_id
            value = each.value()
            session_data[id] = value

        cursor = connection.cursor()



        #add new session in sql
        cursor.execute("UPDATE        home_studysession \
                        SET           start_time = %s, \
                                      end_time = %s, \
                                      date = %s, \
                                      building = %s, \
                                      room_number = %s, \
                                      description = %s \
                        WHERE         seshID = %s",
                                      [session_data['id_' + 'start_time'],
                                      session_data['id_' + 'end_time'],
                                      session_data['id_' + 'date'],
                                      session_data['id_' + 'building'],
                                      session_data['id_' + 'room_number'],
                                      session_data['id_' + 'description'],
                                      seshID])

        #add class of session in sql
        cursor.execute("UPDATE        home_classofsession \
                        SET           class_code = %s \
                        WHERE         seshID = %s",
                                      [session_data['id_' + 'enrolled_class'],
                                      seshID])
