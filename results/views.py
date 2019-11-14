from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse

from .forms import ModuleForm
from .models import YearGrade, ModuleResult, AssessmentResult
from modules.models import Module, AssessmentGroup

def select_module(request):
    """Return page on GET and save assessment results on POST"""
    if request.method == 'POST':
        print(request.POST)

        year = request.POST.get('year')
        year_grade = None
        if year:
            year_grade, created = YearGrade.objects.get_or_create(
                user=request.user,
                year=year
            )
        
        # TODO: check doesn't already exist
        # module_result = ModuleResult.objects.create(
        #     module= ,
        #     year=year_grade,
        #     assessment_group=,
        #     academic_year= ,
        # )

        for assessment_result in self.request.POST:
            if exercise_name not in ['csrfmiddlewaretoken', 'year']:
                # TODO: CHECK DOESN'T ALREADY EXIST
                assessment = AssessmentResult.objects.create(
                    
                )

                weight = self.request.POST.get(exercise_name)
                if weight != '' and weight is not None:
                    ExerciseWeightInput.objects.create(
                        workout=self.get_object(),
                        exercise=exercise,
                        user=user,
                        weight=float(weight)
                    )



    else:
        form = ModuleForm()
    
    return render(request, 'select_module.html', {'form': form})

def get_assessment_group(request):
    """Return a table (in html) of the AssessmentGroups for a given module
    and acadmic year"""
    module_code = request.GET.get('module_code')
    academic_year = request.GET.get('academic_year')

    module = Module.objects.get(module_code=module_code, academic_year=academic_year)
    context = {
        'assessment_groups': module.assessment_groups.all()
    }
    html = render_to_string('get_assessment_group.html', context)
    return HttpResponse(html)

def get_assessments(request):
    """Return a table with the Assessments for the given AssessmentGroup"""
    assessment_group_id = request.GET.get('assessment_group_id')

    assessment_group = AssessmentGroup.objects.get(pk=assessment_group_id)
    context = {
        'assessments': assessment_group.assessments.all()
    }
    html = render_to_string('get_assessments.html', context)
    return HttpResponse(html)
