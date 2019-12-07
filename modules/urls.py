from django.urls import path, include

from . views import start_module_scrape

urlpatterns = [
    path('', start_module_scrape),
]
