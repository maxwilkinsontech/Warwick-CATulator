from django.db import models

class Module(models.Model):
    """
    Stores a single Module entry
    """    
    ACADEMIC_YEARS = (
        ('19/20', '19/20'),
        ('18/19', '18/19'),
        ('17/18', '17/18'),
        ('16/17', '16/17'),
        ('15/16', '15/16'),
        ('14/15', '14/15'),
    )

    level = models.CharField(max_length=15)
    academic_year = models.CharField(max_length=5, choices=ACADEMIC_YEARS, default='19/20')
    faculty = models.CharField(max_length=50)
    module_code = models.CharField(max_length=10)
    module_name = models.CharField(max_length=100)
    cats = models.PositiveSmallIntegerField()

    def __str__(self):
        return '[' + self.module_code + '] ' + self.module_name

class AssessmentGroup(models.Model):
    """
    Stores a single AssessmentGroup entry, related to
    :model:'modules.Module' and 
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    Assessment_group_name = models.CharField(max_length=50)

class Assessment(models.Model):
    """
    Stores a single Assessment entry, related to
    :model:'modules.AssessmentGroup'
    """
    assessment_name = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=4, decimal_places=1)
    uses_worst_result = models.BooleanField(default=False)