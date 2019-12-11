from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('callback/', views.get_access_token, name='get_access_token'),
    path('unknown-modules/,', views.unknown_modules_warnings, name='unknown_modules_warnings')
]
