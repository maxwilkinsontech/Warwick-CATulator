from django.db import models

from users.models import User
from modules.models import Module, AssessmentGroup, Assessment

class YearGrade(models.Model):
    """
    Stores a single Year entry, related to
    :model:'user.User'

    A YearGrade is comprised of several Modules. The weighted sum of the 
    Module marks is calculated to determine the classification of 
    the year for the student.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')

class ModuleResult(models.Model):
    """
    Stores a single ModuleResult entry, related to
    :model:'user.User' and
    :model:'results.YearGrade' and 
    :model:'modules.AssessmentGroup'

    ModuleResult stores the reverse ForeignKeys to the Assessment results
    as well as other data about the Module grade. 
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_results')
    year = models.ForeignKey(YearGrade, on_delete=models.CASCADE, related_name='module_results', null=True)
    assessment_group = models.ForeignKey(AssessmentGroup, on_delete=models.CASCADE, related_name='module_results')
    academic_year = models.CharField(max_length=5, choices=Module.ACADEMIC_YEARS, default='19/20')
    course_year = models.PositiveSmallIntegerField(null=True)

class AssessmentResult(models.Model):
    """
    Stores a single ModuleResult entry, related to
    :model:'results.ModuleResult' and
    :model:'modules.Assessment'

    Stores the Users grade for each Assessment of a AssessmentGroup
    """
    module_result = models.ForeignKey(ModuleResult, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='assessment_results')
    result = models.DecimalField(max_digits=4, decimal_places=1)