from .models import Module, AssessmentGroup, Assessment
from users.models import User

def get_all_modules():
    modules = Module.objects.values_list('module_code', flat=True).distinct()
    print(modules.count())

    modules_19 = Module.objects.filter(academic_year='19/20')#.exclude(module_code__in=modules)
    modules_18 = Module.objects.filter(academic_year='18/19')#.exclude(module_code__in=modules)
    modules_17 = Module.objects.filter(academic_year='17/18')#.exclude(module_code__in=modules)

    print(modules_19.count())
    print(modules_18.count())
    print(modules_17.count())