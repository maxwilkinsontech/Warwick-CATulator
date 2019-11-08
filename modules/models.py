from django.db import models

class Module(models.Model):
    """
    Stores a single Module entry

    Several Modules are taken by student each year. The Assessments of Modules
    can vary for year to year. Not all Modules are weighted the same.
    """    
    ACADEMIC_YEARS = (
        ('19/20', '19/20'),
        ('18/19', '18/19'),
        ('17/18', '17/18'),
        ('16/17', '16/17'),
        ('15/16', '15/16'),
    )

    level = models.CharField(max_length=15)
    academic_year = models.CharField(max_length=5, choices=ACADEMIC_YEARS, default='19/20')
    faculty = models.CharField(max_length=50)
    module_code = models.CharField(max_length=10)
    module_name = models.CharField(max_length=100)

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
    assessment_group_name = models.CharField(max_length=50)
    module_cats = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return self.assessment_group_name

class Assessment(models.Model):
    """
    Stores a single Assessment entry, related to
    :model:'modules.AssessmentGroup'

    An Assessment is one of the ways a Module is graded upon. Each Module
    can have different AssessmentGroups which in turn can have different
    Assessments.
    """
    assessment_group = models.ForeignKey(AssessmentGroup, on_delete=models.CASCADE, related_name='assessments')
    assessment_name = models.CharField(max_length=200)
    percentage = models.DecimalField(max_digits=4, decimal_places=1)
    uses_worst_result = models.BooleanField(default=False)

    def __str__(self):
        return self.assessment_name