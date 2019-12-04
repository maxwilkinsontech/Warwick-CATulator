from django.contrib.auth import login
from django.contrib.auth import logout

def login_view(request):
    """
    This is going to get a token from the Warwick oauth site.

    On first login is going to setup data.
    On subsequent, is going to send to dashboard.
    """
    


    return 

def logout_view(request):
    logout(request)
    return redirect('home')