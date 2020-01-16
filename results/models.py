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

    class Meta:
        ordering = ['-year']

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
        for module in self.module_result_years.select_related('assessment_group').all():
            module_cats = module.assessment_group.module_cats
            total_cats += module_cats
            unweighted_grade += module_cats * module.grade

        if total_cats == 0:
            return total_cats
        return unweighted_grade / total_cats

    def modules(self):
        """
        Return the modules associated with this year ordered by module_code
        """
        return self.module_result_years.prefetch_related('assessment_results').all().order_by('module__module_code')


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
    grade = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def __str__(self):
        return self.module.module_code + ' [' + self.academic_year + ']'

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
        Calculate and save the grade the user has achived in this module so far. This
        method is called every time the user makes a change to the associated 
        AssessmentResults.
        """
        grade = 0
        module_results = self.assessment_results.all()
        
        for result in module_results:
            if result.result is not None:
                grade += (result.result * result.assessment.percentage) / 100

        self.grade = grade
        self.save()

    def result_state(self):
        """
        Return the state of the ModuleResult based upon how many assessments have 
        been completed. Returns 1 if no assessments have results, 2 if all 
        assessments have results and 3 if some assessments have results and some
        don't.
        """
        assessments_completed = 0
        assessments = self.assessment_results.all()

        for assessment in assessments:
            if assessment.result is not None:
                assessments_completed += 1

        if assessments_completed == 0:
            if self.grade != 0:
                return 2
            return 1
        elif assessments_completed == assessments.count():
            return 2
        else:
            return 3


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

@receiver(post_save, sender=AssessmentResult)
def update_module_grade(sender, instance, created, **kwargs):
    if not created:
        instance.module_result.calculate_grade()