from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")
    username = forms.CharField(required=True, label="UIUC Email", help_text="<b>@illinois.edu</b>")

    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_(""),
)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2'
        )


    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name'] # ***self.cleaned_data prevents sql injection
        user.last_name = self.cleaned_data['last_name']
        #print(self.cleaned_data['email'])
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['username'] + '@illinois.edu'


        if commit:
            user.save()

        return user
