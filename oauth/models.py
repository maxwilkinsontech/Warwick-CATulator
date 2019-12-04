from django.db import models

from users.models import User

class Course(models.Model):
    """
    Model to store data about a students course
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200)
    course_year_length = models.IntegerField()