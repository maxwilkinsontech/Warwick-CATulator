from django.urls import path, include

from . views import a

urlpatterns = [
    path('', a),
]
