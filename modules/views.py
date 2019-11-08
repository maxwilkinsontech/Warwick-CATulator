from django.shortcuts import render

from .scrapper import start

def a(request):
    start()
    return render(request, 'index.html')
