from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('callback/', views.get_access_token, name='get_access_token'),
    path('settings/', views.settings, name='settings'),
    path('delete-account/', views.delete_account, name='delete_account'),
]
