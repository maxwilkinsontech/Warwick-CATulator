from django.shortcuts import render
from django.db.models import Sum

from .scrapper import start, count_modules, get_modules
from .models import AssessmentGroup

def start_module_scrape(request):
    # count_modules()
    start()
    # get_modules()
    return render(request, 'index.html')
