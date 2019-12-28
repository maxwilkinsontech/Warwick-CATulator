from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import DetailView, DeleteView, FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic.edit import ProcessFormView
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from .models import YearGrade, ModuleResult, AssessmentResult
from .mixins import ModuleResultPermissionMixin
from .utils import get_or_create_year
from .forms import ModuleForm
from modules.models import Module, AssessmentGroup
from users.models import User


def home(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    """Display the user's Modules"""
    unknown_modules = request.user.unknown_modules.all()

    return render(request, 'dashboard.html', {'unknown_modules': unknown_modules})

@staff_member_required
def user_dashboard(request, user_id):
    """Display a given user's modules"""
    user = get_object_or_404(User, user_id=user_id)
    user.retreive_member_infomation()
    unknown_modules = user.unknown_modules.all()

    return render(request, 'user_dashboard.html', {'unknown_modules': unknown_modules, 'user': user})

class ViewModuleResult(LoginRequiredMixin, ModuleResultPermissionMixin, DetailView):
    """Retrive a ModuleResult and update it on a POST request"""
    template_name = 'view_module/view_module_result.html'
    model = ModuleResult

    def post(self, request, slug):
        module_result = self.get_object()
        year = request.POST.get('year')
        year_grade = get_or_create_year(request.user, year)
        module_result.year = year_grade
        module_result.save()
        
        assessment_results = module_result.assessment_results.all()
        for assessment_result_slug in request.POST:
            if assessment_result_slug not in ['csrfmiddlewaretoken', 'year']:
                result = request.POST.get(assessment_result_slug, '')
                # result may be an empty string
                if result == '':
                    result = None  

                assessment = assessment_results.filter(slug=assessment_result_slug).first()
                
                if assessment is None:
                    continue

                assessment.result = result
                assessment.save()

        return redirect('view_module_result', module_result.slug)


class ViewModuleResultExperimental(LoginRequiredMixin, ModuleResultPermissionMixin, DetailView):
    """Retrive a ModuleResult and display the experimental mode template"""
    template_name = 'view_module/view_module_result_experimental.html'
    model = ModuleResult


@login_required
@require_POST
def delete_module_result(request, slug):
    """Delete a given ModuleResult"""
    module_result = get_object_or_404(ModuleResult, slug=slug)
    module_year = module_result.year
    module_result.delete()
    # Delete associated YearGrade if now empty ModuleResult
    if module_year.is_module_result_empty():
        module_year.delete()

    return redirect('dashboard')

@login_required
def select_module(request):
    """Return page on GET and save Assessment results on POST"""
    if request.method == 'POST':
        # use year value from query params if year input left blank
        year_grade = get_or_create_year(request.user, request.POST.get('year'))

        assessment_group = get_object_or_404(AssessmentGroup, pk=request.POST.get('groups'))
        # check that the ModuleResult doesn't already exist
        if ModuleResult.objects.filter(
            user=request.user,
            year=year_grade,
            module=assessment_group.module
        ).exists():
            return redirect('dashboard')

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

                assessment = AssessmentResult.objects.filter(
                    module_result=module_result,
                    assessment_id=assessment_result_id
                ).first()

                if assessment is None:
                    continue
                
                assessment.result = result
                assessment.save()

        return redirect('view_module_result', module_result.slug)
    else:
        form = ModuleForm()
    
    return render(request, 'add_module/select_module.html', {'form': form})


@login_required
def get_assessment_group(request):
    """Return a table (in html) of the AssessmentGroups for a given module
    and acadmic year"""
    module_code = request.GET.get('module_code')
    academic_year = request.GET.get('academic_year')
    module = get_object_or_404(Module, module_code=module_code, academic_year=academic_year)

    context = {'assessment_groups': module.assessment_groups.all()}
    html = render_to_string('add_module/get_assessment_group.html', context)
    return HttpResponse(html)


@login_required
def get_assessments(request):
    """Return a table with the Assessments for the given AssessmentGroup"""
    assessment_group_id = request.GET.get('assessment_group_id')
    assessment_group = get_object_or_404(AssessmentGroup, pk=assessment_group_id)

    context = {'assessments': assessment_group.assessments.all()}
    html = render_to_string('add_module/get_assessments.html', context)
    return HttpResponse(html)