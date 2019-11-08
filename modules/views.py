from django.shortcuts import render
from django.db.models import Sum

from .scrapper import start
from .models import AssessmentGroup

def a(request):
    start()
    # groups = AssessmentGroup.objects.all()
    # for group in groups:
    #     assessments = group.assessments.all()
    #     sum = 0
    #     for a in assessments:
    #         sum += a.percentage

    #     if 99.9 > sum < 100.1:
    #         print(group.module.module_code)
        


    return render(request, 'index.html')
