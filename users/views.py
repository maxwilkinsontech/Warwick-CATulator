from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from .oauth import obtain_request_token, exchange_access_token


def logout_view(request):
    """
    Logout the current user.
    """
    logout(request)
    return redirect('home')


def login_view(request):
    """
    This is going to get a token from the Warwick oauth site and
    redirect the user to authorize this site.
    """
    url = obtain_request_token()
    return redirect(url)


def get_access_token(request):
    """
    Use the request token from the url params to get a valid access
    token. Then login the user (creating an account if needed).
    """
    oauth_token = request.GET.get('oauth_token')
    user_id = request.GET.get('user_id', 'u1234567')[1:]
    url = request.build_absolute_uri()

    user = exchange_access_token(oauth_token, url, user_id)
    login(request, user)
    
    return redirect('dashboard')