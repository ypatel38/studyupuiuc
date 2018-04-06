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

    def __init__(self, seshID, *args, **kwargs):
        super(EditSessionForm, self).__init__(*args, **kwargs)

        cursor = connection.cursor()
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
        old_session_data["date"] = old_session_sql[0][2]
        old_session_data["building"] = old_session_sql[0][3]
        old_session_data["room_number"] = old_session_sql[0][4]
        old_session_data["description"] = old_session_sql[0][5]
        old_session_data["enrolled_class"] = old_session_sql[0][6]

        connection.close()

        self.fields['enrolled_class'] = forms.CharField(required=True, label="Class", initial = old_session_data["enrolled_class"], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ECE313...' }))
        self.fields['start_time'] = forms.CharField(required=True, label="Start Time", initial = old_session_data["start_time"], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM...' }))
        self.fields['end_time'] = forms.CharField(required=True, label="End Time", initial = old_session_data["end_time"],widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM...' }))
        self.fields['date'] = forms.DateField(required=True, label="Date", initial = old_session_data["date"], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD...' }))
        self.fields['building'] = forms.CharField(required=True, label="Building", initial = old_session_data["building"], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text...' }))
        self.fields['room_number'] = forms.CharField(required=True, label="Room Number", initial = old_session_data["room_number"], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '101...' }))
        self.fields['description'] = forms.CharField(required=False, label="Description", initial = old_session_data["description"], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text...' }))

    def is_valid(self):
        #use regex to determine true of false here
        #STILL NEED TO CHECK IF THE USER OWNS THE STUDY SESSION THEY ARE EDITING
        return True

    def save(self, request, seshID):
        session_data = {}

        # for each in request:
        #     id = each.auto_id
        #     value = each.value()
        #     session_data[id] = value

        cursor = connection.cursor()

        print(request.POST)

        #add new session in sql
        cursor.execute("UPDATE        home_studysession \
                        SET           start_time = %s, \
                                      end_time = %s, \
                                      date = %s, \
                                      building = %s, \
                                      room_number = %s, \
                                      description = %s \
                        WHERE         seshID = %s",
                                      [request.POST['start_time'],
                                      request.POST['end_time'],
                                      request.POST['date'],
                                      request.POST['building'],
                                      request.POST['room_number'],
                                      request.POST['description'],
                                      seshID])

        #add class of session in sql
        cursor.execute("UPDATE        home_classofsession \
                        SET           class_code = %s \
                        WHERE         seshID = %s",
                                      [request.POST['enrolled_class'],
                                      seshID])

        connection.close()
