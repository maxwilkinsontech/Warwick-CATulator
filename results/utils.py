from .models import YearGrade

def get_or_create_year(user, year):
    year_grade = None
    if year is not None:
        year_grade, created = YearGrade.objects.get_or_create(
            user=user,
            year=year
        )
    return year_grade
