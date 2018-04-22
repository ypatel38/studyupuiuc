from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.db import connection #sql
from django.urls import reverse #used for namespaces
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from .tokens import account_activation_token

from accounts.forms import RegistrationForm



# Create your views here.


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

    def get(self, request):
        form = RegistrationForm()
        args = {'form': form}
        #print(form)
        return render(request, self.template_name, args)

    def post(self, request):
        form = RegistrationForm(request.POST)

        if form.is_valid(): #override is_valid later for more restriction
            user = form.save(commit = False)
            user.is_active = False
            form.save()
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user':user, 
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your StudyUP account.'
            to_email = "@".join([form.cleaned_data.get('user'), 'illinois.edu'])
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
            #return redirect(reverse('accounts:login'))
        else:
            return redirect(reverse('accounts:register')) #deal with fail cases here

    def activate(request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            # return redirect('home')
            return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        else:
            return HttpResponse('Activation link is invalid!')

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get(self, request):
        #get enrolled classes
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

        #get other classes
        cursor.execute("SELECT DISTINCT     home_classes.class_code, \
                                            home_classes.class_name \
                        FROM                home_classes \
                        WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                        ORDER BY            home_classes.class_code", [str(request.user)])

        other_classses_arr = cursor.fetchall()

        other_classes = []
        for i in range(len(other_classses_arr)):
            other_classes.append({})
            other_classes[i]['class_code'] = other_classses_arr[i][0]
            other_classes[i]['class_name'] = other_classses_arr[i][1]

        #print(other_classes)

        args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
        return render(request, self.template_name, args)

    def post(self, request):
        #print(request.POST)
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

            #get other classes
            cursor.execute("SELECT DISTINCT     home_classes.class_code, \
                                                home_classes.class_name \
                            FROM                home_classes \
                            WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            other_classses_arr = cursor.fetchall()

            other_classes = []
            for i in range(len(other_classses_arr)):
                other_classes.append({})
                other_classes[i]['class_code'] = other_classses_arr[i][0]
                other_classes[i]['class_name'] = other_classses_arr[i][1]


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


            #get other classes
            cursor.execute("SELECT DISTINCT     home_classes.class_code, \
                                                home_classes.class_name \
                            FROM                home_classes \
                            WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            other_classses_arr = cursor.fetchall()

            other_classes = []
            for i in range(len(other_classses_arr)):
                other_classes.append({})
                other_classes[i]['class_code'] = other_classses_arr[i][0]
                other_classes[i]['class_name'] = other_classses_arr[i][1]

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


            #get other classes
            cursor.execute("SELECT DISTINCT     home_classes.class_code, \
                                                home_classes.class_name \
                            FROM                home_classes \
                            WHERE               home_classes.class_code NOT IN(SELECT accounts_enrolledin.class_code FROM accounts_enrolledin WHERE accounts_enrolledin.netID = %s) \
                            ORDER BY            home_classes.class_code", [str(request.user)])

            other_classses_arr = cursor.fetchall()

            other_classes = []
            for i in range(len(other_classses_arr)):
                other_classes.append({})
                other_classes[i]['class_code'] = other_classses_arr[i][0]
                other_classes[i]['class_name'] = other_classses_arr[i][1]

            #print(other_classes)
            cursor.close()

            args = {'user': request.user, 'enrolled_classes': enrolled_classes, 'other_classes': other_classes}
            return render(request, self.template_name, args)
