import random
import string

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

from modules.models import Module, AssessmentGroup, Assessment, UndefinedModule
from users.models import User

class YearGrade(models.Model):
    """
    Stores a single Year entry, related to
    :model:'user.User'

    A YearGrade is comprised of several Modules. The weighted sum of the Module
    marks is calculated to determine the classification of the year.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    year = models.PositiveSmallIntegerField()

    def __str__(self):
        return '[' + str(self.year) + ']' + ' ' + self.user.get_full_name()

    def is_module_result_empty(self):
        return self.module_result_years.count() == 0

    def calculate_grade(self):
        """
        Calculate the weighted percentage grade for this year.
        """
        total_cats = 0
        unweighted_grade = 0
        for module in self.module_result_years.all():
            total_cats += module.assessment_group.module_cats
            unweighted_grade += module.assessment_group.module_cats * module.calculate_grade() 

        if total_cats == 0:
            return total_cats
        return unweighted_grade / total_cats

class ModuleResult(models.Model):
    """
    Stores a single ModuleResult entry, related to
    :model:'user.User' and
    :model:'results.YearGrade' and 
    :model:'modules.Module' and 
    :model:'modules.AssessmentGroup'

    ModuleResult stores the reverse ForeignKeys to the Assessment results
    as well as other data about the Module grade. 
    """
    slug = models.SlugField(max_length=8, unique=True, blank=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_results')
    year = models.ForeignKey(YearGrade, on_delete=models.CASCADE, related_name='module_result_years', null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module_result_modules')
    assessment_group = models.ForeignKey(AssessmentGroup, on_delete=models.CASCADE, related_name='module_result_groups')
    academic_year = models.CharField(max_length=5, choices=Module.ACADEMIC_YEARS, default='19/20')

    class Meta:
        ordering = ['module']

    def __str__(self):
        return self.module.module_code

    def save(self, *args, **kwargs):
        """
        Generate a random 8 digit slug as this is visable in the url.
        """
        if not self.slug:
            while True:
                slug = ''.join(random.choice(string.digits) for _ in range(8))
                if not ModuleResult.objects.filter(slug=slug).exists():
                    break
            self.slug = slug

        super(ModuleResult, self).save(*args, **kwargs)

    def calculate_grade(self):
        """
        Calculate the grade the user has achived in this module so far. 
        """
        grade = 0
        module_results = self.assessment_results.all()
        
        for result in module_results:
            if result.result is not None:
                grade += (result.result * result.assessment.percentage) / 100

        return grade


class AssessmentResult(models.Model):
    """
    Stores a single ModuleResult entry, related to
    :model:'results.ModuleResult' and
    :model:'modules.Assessment'

    Stores the Users grade for each Assessment of a AssessmentGroup
    """
    slug = models.SlugField(max_length=8, unique=True, blank=True, editable=False)
    module_result = models.ForeignKey(ModuleResult, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    result = models.DecimalField(max_digits=4, decimal_places=1, null=True)

    def __str__(self):
        return self.assessment.assessment_name

    def save(self, *args, **kwargs):
        if not self.slug:
            while True:
                slug = ''.join(random.choice(string.digits) for _ in range(8))
                if not AssessmentResult.objects.filter(slug=slug).exists():
                    break
            self.slug = slug

        super(AssessmentResult, self).save(*args, **kwargs)

@receiver(post_save, sender=ModuleResult)
def add_assessments_after_created(sender, instance, created, **kwargs):
    if created:
        assessments = instance.assessment_group.assessments.all()
        for assessment in assessments:
            AssessmentResult.objects.create(
                module_result=instance,
                assessment_id=assessment.id,
            )

@receiver(post_save, sender=Module)
def undefined_module_to_module(sender, instance, created, **kwargs):
    """
    Whenever a new module is created, check if a user needs it added to
    their profile.
    """
    if created:
        undefined_modules = UndefinedModule.objects.filter(module_code=instance.module_code)
        if undefined_modules.exists():
            for module in undefined_modules:
                module_info = (
                    Module
                    .objects
                    .filter(module_code=module.module_code)
                    .order_by('id')
                    .first()
                )

                assessment_group = module_info.assessment_groups.filter(
                    assessment_group_code=module.assessment_group_code
                )

                ModuleResult.objects.create(
                    user=module.user,
                    year=module.year,
                    module=module_info,
                    assessment_group=assessment_group,
                    academic_year=module.academic_year
                )