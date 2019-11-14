from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse

from .forms import ModuleForm
from .models import YearGrade, ModuleResult, AssessmentResult
from modules.models import Module, AssessmentGroup

def home(request):
    return render(request, 'index.html')

def dashboard(request):
    """Display the user's Modules"""
    return render(request, 'dashboard.html')

def select_module(request):
    """Return page on GET and save Assessment results on POST"""
    if request.method == 'POST':
        year = request.POST.get('year')
        year_grade = None
        if year:
            year_grade, created = YearGrade.objects.get_or_create(
                user=request.user,
                year=year
            )

        assessment_group = get_object_or_404(AssessmentGroup, pk=request.POST.get('groups'))
        module_result, assessment_group_created = ModuleResult.objects.get_or_create(
            user=request.user,
            year=year_grade,
            module=assessment_group.module,
            assessment_group=assessment_group,
            academic_year=request.POST.get('academic_year')
        )

        for assessment_result_id in request.POST:
            if assessment_result_id not in ['csrfmiddlewaretoken', 'year', 'module_code', 'academic_year', 'groups']:
                result = request.POST.get(assessment_result_id, '')
                if result == '':
                    result = None

                try:
                    assessment = AssessmentResult.objects.get(
                        module_result=module_result,
                        assessment_id=assessment_result_id
                    )
                    assessment.result = result
                    assessment.save()
                except AssessmentResult.DoesNotExist:
                    assessment = AssessmentResult.objects.create(
                        module_result=module_result,
                        assessment_id=assessment_result_id,
                        result=result
                    )

        return redirect('dashboard')
    else:
        form = ModuleForm()
    
    return render(request, 'select_module.html', {'form': form})

def get_assessment_group(request):
    """Return a table (in html) of the AssessmentGroups for a given module
    and acadmic year"""
    module_code = request.GET.get('module_code')
    academic_year = request.GET.get('academic_year')
    module = Module.objects.get(module_code=module_code, academic_year=academic_year)

    context = {'assessment_groups': module.assessment_groups.all()}
    html = render_to_string('get_assessment_group.html', context)
    return HttpResponse(html)

def get_assessments(request):
    """Return a table with the Assessments for the given AssessmentGroup"""
    assessment_group_id = request.GET.get('assessment_group_id')
    assessment_group = AssessmentGroup.objects.get(pk=assessment_group_id)

    context = {'assessments': assessment_group.assessments.all()}
    html = render_to_string('get_assessments.html', context)
    return HttpResponse(html)
