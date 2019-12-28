from modules.models import Course, Module, AssessmentGroup, UndefinedModule
from results.models import ModuleResult, YearGrade
from users.models import User, TabulaDump


TABULAR_URL = 'https://tabula.warwick.ac.uk/api/v1/member/me'

def retreive_member_infomation(user, created=False):
    """
    This method is used to populate the user's profile with infomation from
    Tabula. The argument 'created' is used to tell the method if the user's 
    information needs to be gathered for the first time or updated.
    """
    oauth = user.get_oauth_session()
    response = oauth.request("GET", TABULAR_URL)
    data = response.json()['member']
    save_json(user, data)
    # save basic user info
    user.first_name = data['firstName']
    user.last_name = data['lastName']
    user.email = data['email']
    user.save()
    # save user's course info
    save_course_infomation(user, data, created)

def save_json(user, data):
    """
    Save the returned json data from Tabula to the database.
    """
    TabulaDump.objects.create(
        user=user,
        data=data
    )

def save_course_infomation(user, data, created):
    """
    Retrive infomation about the student's course. May be more than 1 course. 
    Get user's active course: marked with mostSignificant=true.
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

    Course.objects.get_or_create(
        user=user,
        course_name=course_name,
        course_year_length=course_year_length
    )

    years = get_years(user, course['studentCourseYearDetails'])
    modules = course['moduleRegistrations']

    if created:
        save_modules(user, years, modules)
    else:
        update_modules(user, years, modules)
    
def update_modules(user, years, modules):
    """
    This method is used to update a user's information about their course. It is
    called whenever they login via the web sign-on. No action is taken on any 
    conflicts - the original remains the same. Only modules that are not already
    in the user's profile are added.
    """
    for module in modules:
        poss_current_module = user.module_results.filter(
            module__module_code=module['module']['code'].upper()
        )
        if not poss_current_module.exists():
            save_module(user, years, module)

def save_modules(user, years, modules):
    """
    Create the appropriate models for the modules the student is taking.
    """
    for module in modules:
        save_module(user, years, module)

def save_module(user, years, module):
    """
    Create the appropriate models for the modules the student is taking.
    """
    module_code = module['module']['code']
    module_cats = module['cats']
    academic_year = module['academicYear']
    assessment_group_code = module['assessmentGroup']
    # get the data about the module
    module_info = (
        Module
        .objects
        .filter(module_code=module_code.upper(), academic_year=academic_year)
        .order_by('id')
        .first()
    )
    if module_info is None:
        module_info = (
            Module
            .objects
            .filter(module_code=module_code.upper(), academic_year='19/20')
            .order_by('id')
            .first()
        )
        if module_info is None:
            UndefinedModule.objects.create(
                user=user,
                year=years[academic_year].year,
                module_code=module_code,
                assessment_group_code=assessment_group_code,
                academic_year=academic_year
            )      
            return
    # get the modules assessments and match to the correct one
    assessment_groups = module_info.assessment_groups.all()
    assessment_group = (
        assessment_groups
        .filter(assessment_group_code=assessment_group_code, module_cats=module_cats)
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
                assessment_group_code=assessment_group_code,
                academic_year=academic_year
            )
            return       

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