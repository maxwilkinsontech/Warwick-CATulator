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
    Redirect the user to authorize the request token via logging in to their 
    Warwick ITS account. They will be directed back to the callback argument.
    """
    # Uncomment when not running locally.
    # url = obtain_request_token(callback='http://178.62.83.252:8000/callback/')
    url = obtain_request_token()
    return redirect(url)

def get_access_token(request):
    """
    Use the request token from the url params to get a valid access token. Then 
    login the user (creating an account if needed) and redirect to their 
    dashboard.
    """
    oauth_token = request.GET.get('oauth_token')
    user_id = request.GET.get('user_id', 'u1234567')[1:] # remove 'u' prefix
    url = request.build_absolute_uri()

    user = exchange_access_token(oauth_token, url, user_id)
    login(request, user)
    
    return redirect('dashboard')
