from django.shortcuts import render

from .tabular_api import retreive_member_infomation

def test(request):

    retreive_member_infomation()

    return render(request, 'test.html')