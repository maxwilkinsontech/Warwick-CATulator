from django.shortcuts import render
from django.db.models import Sum

from .scrapper import start, count_modules
from .models import AssessmentGroup

def a(request):
    count_modules()

    return render(request, 'index.html')
