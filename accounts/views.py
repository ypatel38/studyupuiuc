from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.db import connection #sql
from django.urls import reverse #used for namespaces


from accounts.forms import RegistrationForm



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

        for i in range(len(enrolled_classes_arr)):
            enrolled_classes.append(enrolled_classes_arr[i][0])

        #print(enrolled_classes)

        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT     home_classes.class_code \
                        FROM                accounts_enrolledin, \
                                            home_classes\
                        WHERE               home_classes.class_code <> accounts_enrolledin.class_code AND \
                                            accounts_enrolledin.netID = %s \
                        ORDER BY            home_classes.class_code", [str(request.user)])

        other_classses_arr = cursor.fetchall()

        other_classes = []

        for i in range(len(other_classses_arr)):
            other_classes.append(other_classses_arr[i][0])

        #print(other_classes)

        args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
        return render(request, self.template_name, args)

    def post():
        pass
