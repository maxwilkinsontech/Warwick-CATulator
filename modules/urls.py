from django.urls import path, include

from . views import update_unknown_modules, start_module_scrape

urlpatterns = [
    path('', start_module_scrape),
    path('update-unknown-modules/', update_unknown_modules),
]
