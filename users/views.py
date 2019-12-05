from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from .oauth import obtain_request_token, exchange_access_token


def login_view(request):
    """
    This is going to get a token from the Warwick oauth site.

    On first login is going to setup data.
    On subsequent, is going to send to dashboard.
    """
    url = obtain_request_token()
    return redirect(url)

def logout_view(request):
    logout(request)
    return redirect('home')

def get_access_token(request):
    """
    Use the request token in the url params to get a valid access
    token.
    """
    oauth_token = request.GET.get('oauth_token')
    user_id = request.GET.get('user_id')

    print(oauth_token)
    print(user_id)

    exchange_access_token(oauth_token, user_id)
    
    return redirect('dashboard')