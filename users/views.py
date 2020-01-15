from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from .oauth import obtain_request_token, exchange_access_token


@login_required
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
    # url = obtain_request_token(callback='https://warwickcatulator.co.uk/callback')
    url = obtain_request_token(callback='http://127.0.0.1:8000/callback')
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

@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
@require_POST
def delete_account(request):
    """
    To complie to GDPR, delete the user's account and all data associated with it.
    """
    request.user.delete()
    return redirect('home')