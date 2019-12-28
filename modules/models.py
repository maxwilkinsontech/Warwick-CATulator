from django.db import models

from users.models import User


class Course(models.Model):
    """
    Stores a single Course entry, related to
    :model:'users.User'

    Model to store data about a student's course.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200)
    course_year_length = models.IntegerField()

    def __str__(self):
        return '[' + self.course_name + '] ' + self.user.get_full_name()

class Module(models.Model):
    """Stores a single Module entry.

    Several Modules are taken by student each year. The Assessments of
    Modules can vary for year to year. Not all Modules are weighted the
    same.
    """
    ACADEMIC_YEARS = (
        ('19/20', '19/20'),
        ('18/19', '18/19'),
        ('17/18', '17/18'),
    )

    academic_year = models.CharField(max_length=5, choices=ACADEMIC_YEARS, default='19/20')
    faculty = models.CharField(max_length=100)
    module_code = models.CharField(max_length=50)
    module_name = models.CharField(max_length=200)

    def __str__(self):
        return '[' + self.module_code + '] ' + self.module_name

class AssessmentGroup(models.Model):
    """
    Stores a single AssessmentGroup entry, related to
    :model:'modules.Module'

    A Module can have several AssessmentGroups, each taken by different
    cohorts of students. Each AssessmentGroup can be made up of different 
    Assessments. 
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assessment_groups')
    assessment_group_name = models.CharField(max_length=200)
    assessment_group_code = models.CharField(max_length=5)
    module_cats = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return self.assessment_group_name

    class Meta:
        ordering = ['assessment_group_name']

class Assessment(models.Model):
    """
    Stores a single Assessment entry, related to
    :model:'modules.AssessmentGroup'

    An Assessment is one of the ways a Module is graded upon. Each Module can 
    have different AssessmentGroups which in turn can have different Assessments.
    """
    assessment_group = models.ForeignKey(AssessmentGroup, on_delete=models.CASCADE, related_name='assessments')
    assessment_name = models.CharField(max_length=200)
    percentage = models.DecimalField(max_digits=4, decimal_places=1)
    # uses_worst_result = models.BooleanField(default=False)

    def __str__(self):
        return self.assessment_name

class UndefinedModule(models.Model):
    """
    This model is for modules that don't have an associated Module. It will be 
    used for telling me what modules need creating and for which users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unknown_modules')
    year = models.IntegerField()
    module_code = models.CharField(max_length=50)
    assessment_group_code = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.module_code