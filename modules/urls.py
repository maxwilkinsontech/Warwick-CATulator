from django.urls import path, include

from . views import update_unknown_modules

urlpatterns = [
    path('update-unknown-modules/', update_unknown_modules),
]
