from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.generic.edit import DeletionMixin
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import ModuleForm
from .models import YearGrade, ModuleResult, AssessmentResult
from .mixins import ModuleResultPermissionMixin
from .utils import get_or_create_year
from modules.models import Module, AssessmentGroup


def home(request):
    return render(request, 'index.html')


def dashboard(request):
    """Display the user's Modules"""
    user = request.user
    years = user.grades.all()
    # results = user.module_results.all()

    context = {
        'years': years
    }
    # context = {'years': years}
    # for year in years:
    #     context[str(year.year)] = results.filter(year=year)
    #     results.exclude(year=year)
    # context['unspecified_year'] = results

    return render(request, 'dashboard.html', context)


class ViewModuleResult(ModuleResultPermissionMixin, UpdateView):
    """Retrive a ModuleResult and update it on a POST request"""
    template_name = 'view_module_result.html'
    model = ModuleResult
    success_url = reverse_lazy('dashboard')
    fields = ['year'] # not used but to prevent exception

    def post(self, request, slug):
        year = request.POST.get('year')
        get_or_create_year(request.user, year)
        
        for assessment_result_id in request.POST:
            if assessment_result_id not in ['csrfmiddlewaretoken', 'year']:
                result = request.POST.get(assessment_result_id, None)

                try:
                    assessment = AssessmentResult.objects.get(
                        module_result=module_result,
                        assessment_id=assessment_result_id
                    )
                    assessment.result = result
                    assessment.save()
                except AssessmentResult.DoesNotExist:
                    continue



@require_http_methods(['POST'])
def delete_module_result(request, slug):
    """Delete a given ModuleResult"""
    if request.method == 'POST':
        module_result = get_object_or_404(ModuleResult, slug=slug)
        module_year = module_result.year
        module_result.delete()
        # Delete associated YearGrade if now empty ModuleResult
        if module_year.is_module_result_empty():
            module_year.delete()

        return redirect('dashboard')  


def select_module(request):
    """Return page on GET and save Assessment results on POST"""
    if request.method == 'POST':
        # use year value from query params if year input left blank
        year_post = request.POST.get('year')
        year_get = request.GET.get('year')
        year = year_post if year_post is not None else year_get
        year_grade = get_or_create_year(request.user, year)

        assessment_group = get_object_or_404(AssessmentGroup, pk=request.POST.get('groups'))
        module_result, assessment_group_created = ModuleResult.objects.get_or_create(
            user=request.user,
            year=year_grade,
            module=assessment_group.module,
            assessment_group=assessment_group,
            academic_year=request.POST.get('academic_year')
        )
        # iterate through assessment results and create/save them.
        for assessment_result_id in request.POST:
            if assessment_result_id not in ['csrfmiddlewaretoken', 'year', 'module_code', 'academic_year', 'groups']:
                result = request.POST.get(assessment_result_id, '')
                # result may be an empty string
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

    module = get_object_or_404(Module, module_code=module_code, academic_year=academic_year)

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
