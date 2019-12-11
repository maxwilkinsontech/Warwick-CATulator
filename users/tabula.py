from modules.models import Course, Module, AssessmentGroup, UndefinedModule
from results.models import ModuleResult, YearGrade
from users.models import User


TABULAR_URL = 'https://tabula.warwick.ac.uk/api/v1/member/me'

def retreive_member_infomation(user, created=True):
    """
    This method is used to populate the user's profile with infomation from
    Tabula. The argument 'created' is used to tell the method if the user's 
    information needs to be gathered for the first time or updated.
    """
    oauth = user.get_oauth_session()
    response = oauth.request("GET", TABULAR_URL)
    data = response.json()['member']
    # save basic user info
    user.first_name = data['firstName']
    user.last_name = data['lastName']
    user.email = data['email']
    user.save()
    # save user's course info
    if created:
        save_course_infomation(user, data)
    else:
        update_course_infomation(user, data)

def save_course_infomation(user, data):
    """
    Retrive infomation about the student's course. May be more than 1 course. 
    Get user's active course: marked with mostSignificant=true.
    """
    courses = data['studentCourseDetails']
    course = courses[0]
    if len(courses) > 1:
        for poss_course in courses:
            if course['mostSignificant']:
                course = poss_course 
                break

    course_year_length = course['courseYearLength']
    course_name = course['course']['name']

    Course.objects.get_or_create(
        user=user,
        course_name=course_name,
        course_year_length=course_year_length
    )

    courses = course['moduleRegistrations']
    courses.append(
        {'academicYear': '19/20',
        'assessmentGroup': 'X',
        'cats': 15.0,
        'module': {'adminDepartment': {'code': 'cs', 'name': 'DCS'},
                    'code': 'XXXXX',
                    'name': 'XXXXX'},
        'occurrence': 'A',
        'status': 'Core'},
    )

    years = get_years(user, course['studentCourseYearDetails'])
    # save_modules(user, years, course['moduleRegistrations'])
    save_modules(user, years, courses)

def save_modules(user, years, modules):
    """
    Create the appropriate models for the modules the student is taking.
    """
    for module in modules:
        module_code = module['module']['code']
        academic_year = module['academicYear']
        assessment_group = module['assessmentGroup']
        
        module_info = (
            Module
            .objects
            .filter(module_code=module_code.upper())
            .order_by('id')
            .first()
        )
        if module_info is None:
            UndefinedModule.objects.create(
                user=user,
                year=years[academic_year].year,
                module_code=module_code,
                assessment_group_code=assessment_group,
                academic_year=academic_year
            )      
            continue
        # TODO: FILTER BY CATS TOO
        assessment_groups = module_info.assessment_groups.all()
        assessment_group = (
            assessment_groups
            .filter(assessment_group_code=assessment_group)
            .order_by('id')
            .first()
        )
        if assessment_group is None:
            if assessment_groups.count() == 1:
                assessment_group = assessment_groups.first()
            else:
                UndefinedModule.objects.create(
                    user=user,
                    year=years[academic_year].year,
                    module_code=module_code,
                    assessment_group_code=assessment_group,
                    academic_year=academic_year
                )
                continue       

        ModuleResult.objects.create(
            user=user,
            year=years[academic_year],
            module=module_info,
            assessment_group=assessment_group,
            academic_year=academic_year
        )

def get_years(user, years):
    """
    Return a dict with the academic year and corrosponding YearGrade of the
    user's course.
    """
    years_dict = {}

    for year in years:
        year_grade, created = YearGrade.objects.get_or_create(
            user=user,
            year=year['yearOfStudy']
        )
        years_dict[year['academicYear']] = year_grade

    return years_dict

def update_course_infomation(user, data):
    """
    This method is used to update a user's information about their course. It is
    called whenever they login via the web sign-on. Any comflicts are handled by...
    """
    pass