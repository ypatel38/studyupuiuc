import re #regex

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')
        print(path)

        url_is_exempt = any(url.match(path) for url in EXEMPT_URLS)
        print(request.user.is_authenticated)
        if request.user.is_authenticated and url_is_exempt: #logged in and accessing not logged in pages
            if not path == reverse('accounts:logout').lstrip('/'):
                return redirect(settings.LOGIN_REDIRECT_URL)

        elif request.user.is_authenticated or url_is_exempt: #logged in and accessing loggin pages or not logged in and accessing not logged in pages
            return None

        else: #not logged in and accessing logged in pages
            return redirect(settings.LOGIN_URL)
