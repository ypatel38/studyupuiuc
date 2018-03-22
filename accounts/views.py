from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.urls import reverse #used for namespaces

from accounts.forms import RegistrationForm



# Create your views here.
class RegisterView(TemplateView):
    template_name = "accounts/login.html"

    def get(self, request):
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'accounts/register.html', args)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('accounts:login'))
        else:
            return redirect(reverse('accounts:register')) #deal with fail cases here
