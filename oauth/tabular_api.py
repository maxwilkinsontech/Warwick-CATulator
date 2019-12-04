import requests

from .models import Course
from users.models import User
from results.models import ModuleResult
from modules.models import Module

TABULAR_ENDPOINT = 'https://tabula.warwick.ac.uk/api/v1/'

def retreive_member_infomation(university_id=1801383):
    url = TABULAR_ENDPOINT + 'member/' + str(university_id)
    request_headers = {
        'Authorization': 'Basic MTgwMTM4MzpIb2NrZXkxMldpbGtpbnNvbjM1d2Fyd2ljaw=='
    }

    response = requests.get(url, headers=request_headers)
    json_response = response.json()['member']

    user = save_student_infomation(json_response)
    save_course(user, json_response)

def save_student_infomation(data):
    """
    Store infomation about the student
    """
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    user, created = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=None
    )

    return user

def save_course(user, data):
    """
    Retrive infomation about the student's course.
    May be more than 1 course. Active course marked with mostSignificant=true
    """
    courses = data['studentCourseDetails']

    course = courses[0]
    if len(courses) > 1:
        for poss_course in courses:
            if course['mostSignificant'] == True:
                course = poss_course 
                break

    course_year_length = course['courseYearLength']
    course_name = course['course']['name']

    Course.objects.create(
        user=user,
        course_name=course_name,
        course_year_length=course_year_length
    )

    save_modules(user, course['moduleRegistrations'])

def save_modules(user, modules):
    """
    Create the appropriate models for the modules the student is taking
    """
    for module in modules:
        module_code = module['module']['code']
        module_name = module['module']['name']
        module_cats = module['cats']
        academic_year = module['academicYear']
        assessment_group = module['assessmentGroup']
        # get the module from the database
        try:
            module_info = Module.objects.get(
                module_code=module_code, 
                academic_year=academic_year
            )
        except Module.DoesNotExist:
            print('Module' + str(module_code) + ' does not exist')
            continue

        # get the assessment group from the database
        

        # create the ModuleResult for the student
        module_object = ModuleResult.objects.create(
            user=user,
            year=,
            module=module_info,
            assessment_group=,
            academic_year=academic_year
        )

retreive_member_infomation()