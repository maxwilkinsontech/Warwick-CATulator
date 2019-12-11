"""
In order to get the data on each module, I have scrapped Warwick's Module
catalog (https://warwick.ac.uk/services/aro/dar/quality/modules/).
"""
# for multiprocessing to work
import django
django.setup()
# imports
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from multiprocessing import Pool

from .models import Module, AssessmentGroup, Assessment
from users.models import User

MODULES_URL = 'https://tabula.warwick.ac.uk/api/v1/module'

def get_1920_diff_modules():
    """
    This method attempts to get the modules that aren't in the 19/20 year but 
    are the others
    """
    modules_20 = Module.objects.filter(academic_year='19/20').values_list('module_code', flat=True).distinct()
    modules_19 = Module.objects.filter(academic_year='18/19').values_list('module_code', flat=True).distinct()
    modules_18 = Module.objects.filter(academic_year='17/18').values_list('module_code', flat=True).distinct()

    print(modules_20.count())
    print(modules_19.count())
    print(modules_18.count())

    diff_19 = [m for m in set(modules_19) if m not in set(modules_18)]
    diff_18 = [m for m in set(modules_20) if m not in set(modules_18)]

    diff = set(diff_19 + diff_18)

    print(len(diff))

    p = Pool(4)
    returned_module_codes = p.map(save_diff, diff)

def save_diff(module_code):
    # user = User.objects.get(email="Max.Wilkinson@warwick.ac.uk")
    # oauth = user.get_oauth_session()
    # url = 'https://tabula.warwick.ac.uk/api/v1/module/' + str(module_code)
    # response = oauth.request("GET", url)
    # department_code = response.json()['module']['adminDepartment']['code']

    url = 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201718/undergraduate-1718/undergraduate-copy/' + module_code[:2] + '/' + module_code
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        module_info = soup.find('ul', class_='list-unstyled').findAll('li')

        # Get the Module info and create it 
        module_code = module_info[0].text.split(': ')[1]
        module_name = module_info[1].text.split(': ')[1]
        module_faculty = module_info[2].text.split(': ')[1]

        if not Module.objects.filter(module_code=module_code, academic_year='17/18').exists():

            module = Module.objects.create(
                academic_year='17/18',
                module_code=module_code,
                module_name=module_name,
            )

            # Get the assessment infomation for the module
            assessment_groups_table = soup.find('table', class_='table table-striped').findAll('tbody')

            for body in assessment_groups_table:
                assessment_groups = body.findAll('tr')
                # create a dictionary, key is the name of the AssessmentGroup and value
                # is a list of Assessments
                assessment_groups_dict = {}
                prev_assessment_name = None
                for row in assessment_groups[1:]:
                    cols = row.findAll('td')
                    assessment_name = cols[0].text.strip()

                    if len(assessment_name) > 1:
                        cats = assessment_groups[0].find('th').text.split(' ')[0]
                        assessment_groups_dict[assessment_name] = [[cats, cols[1].text, cols[2].text]]
                        prev_assessment_name = assessment_name
                    else:
                        assessment_groups_dict.get(prev_assessment_name, []).append([None, cols[1].text, cols[2].text])
                
                for key, value in assessment_groups_dict.items():
                    assessment_group = AssessmentGroup.objects.create(
                        module=module,
                        assessment_group_name=key,
                        assessment_group_code=key.split(' ', 1)[0],
                        module_cats=value[0][0]
                    )

                    for assessment in value:
                        Assessment.objects.create(
                            assessment_group=assessment_group,
                            assessment_name=assessment[1],
                            percentage=float(assessment[2].strip('%'))
                        )
    except:
        print(str(module_code) + ' : ' + str(module_code)[:2])



def count_modules():
    user = User.objects.get(email="Max.Wilkinson@warwick.ac.uk")
    oauth = user.get_oauth_session()
    response = oauth.request("GET", MODULES_URL)
    print(len([x for x in response.json()['modules'] if x['active']]))


def get_modules():
    """
    Get all modules from Tabula.
    """
    user = User.objects.get(email="Max.Wilkinson@warwick.ac.uk")
    oauth = user.get_oauth_session()
    response = oauth.request("GET", MODULES_URL)
    modules = response.json()['modules']

    unfound_module = []

    p = Pool(5)
    returned_module_codes = p.map(save_module, modules)

    # for module in modules:
    #     returned_module_code = save_module(module)
    #     if returned_module_code is not None:
    #         unfound_module.append(returned_module_code)

    unfound_modules = [x for x in returned_module_codes if x is not None]
    print(*unfound_modules)
    print(len(unfound_modules))

def save_module(module):
    """
    Given a module json object, get its data and save it to the database.
    """
    module_name = module['name']
    module_code = module['code']
    department_name = module['adminDepartment']['name']
    department_code = module['adminDepartment']['code']

    url = (
        'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/'
        + module_code[:2]
        + '/'
        + module_code
    )

    response = requests.get(url)

    if response.status_code == 404:
        print('404: ' + str(module_code))
        return module_code
        
    soup = BeautifulSoup(response.text, 'html.parser')

    if not Module.objects.filter(module_code=module_code, academic_year='18/19').exists():
        # Get the assessment infomation for the module
        assessment_groups_table = soup.find('table', class_='table table-striped').findAll('tbody')
        
        if assessment_groups_table is None:
            print('agt: ' + str(module_code))
            return module_code

        module = Module.objects.create(
            academic_year='18/19',
            faculty=department_name,
            module_code=module_code,
            module_name=module_name
        )

        for body in assessment_groups_table:
            assessment_groups = body.findAll('tr')
            # create a dictionary, key is the name of the AssessmentGroup and value
            # is a list of Assessments
            assessment_groups_dict = {}
            prev_assessment_name = None
            for row in assessment_groups[1:]:
                cols = row.findAll('td')
                assessment_name = cols[0].text.strip()

                try: 
                    if len(assessment_name) > 1:
                        cats = assessment_groups[0].find('th').text.split(' ')[0]
                        assessment_groups_dict[assessment_name] = [[cats, cols[1].text, cols[2].text]]
                        prev_assessment_name = assessment_name
                    else:
                        assessment_groups_dict.get(prev_assessment_name, []).append([None, cols[1].text, cols[2].text])
                except IndexError:
                    module.delete()
                    print('ie: ' + str(module_code))
                    return module_code

            for key, value in assessment_groups_dict.items():
                assessment_group = AssessmentGroup.objects.create(
                    module=module,
                    assessment_group_name=key,
                    assessment_group_code=key.split(' ', 1)[0],
                    module_cats=value[0][0]
                )

                for assessment in value:
                    Assessment.objects.create(
                        assessment_group=assessment_group,
                        assessment_name=assessment[1],
                        percentage=float(assessment[2].strip('%'))
                    )
        print('******' + str(module_code))
    return

def get_faculties(request_data):
    """Get all the factulties for the undergraduate."""
    response = requests.get(request_data[2])
    soup = BeautifulSoup(response.text, 'html.parser')

    for ultag in soup.findAll('ul', class_='list-unstyled'):
        for litag in ultag.findAll('li'):
            faculty_modules_link = litag.find('a', {}).get('href', None)
            if faculty_modules_link is None:
                print('faculty_modules_link is None')
                continue
            get_faculty_modules(request_data, faculty_modules_link)

def get_faculty_modules(request_data, link):
    url = request_data[2] + link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for ultag in soup.findAll('ul', class_='list-unstyled'):
        for litag in ultag.findAll('li'):
            module_link = litag.find('a').get('href', None)
            if module_link is None:
                print('module_link is None')
                continue
            try:
                get_module_info(request_data, link, module_link)
            except AttributeError:
                print('get_module_info AttributeError')
                continue

def get_module_info(request_data, link, module_link):
    url = request_data[2] + module_link[:2] + '/' + module_link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    module_info = soup.find('ul', class_='list-unstyled').findAll('li')

    # Get the Module info and create it 
    module_code = module_info[0].text.split(': ')[1]
    module_name = module_info[1].text.split(': ')[1]
    module_faculty = module_info[2].text.split(': ')[1]

    if not Module.objects.filter(module_code=module_code, academic_year=request_data[0]).exists():

        module = Module.objects.create(
            academic_year=request_data[0],
            module_code=module_code,
            module_name=module_name,
        )

        print(module_link)

        # Get the assessment infomation for the module
        assessment_groups_table = soup.find('table', class_='table table-striped').findAll('tbody')

        for body in assessment_groups_table:
            assessment_groups = body.findAll('tr')
            # create a dictionary, key is the name of the AssessmentGroup and value
            # is a list of Assessments
            assessment_groups_dict = {}
            prev_assessment_name = None
            for row in assessment_groups[1:]:
                cols = row.findAll('td')
                assessment_name = cols[0].text.strip()

                if len(assessment_name) > 1:
                    cats = assessment_groups[0].find('th').text.split(' ')[0]
                    assessment_groups_dict[assessment_name] = [[cats, cols[1].text, cols[2].text]]
                    prev_assessment_name = assessment_name
                else:
                    assessment_groups_dict.get(prev_assessment_name, []).append([None, cols[1].text, cols[2].text])
            
            for key, value in assessment_groups_dict.items():
                assessment_group = AssessmentGroup.objects.create(
                    module=module,
                    assessment_group_name=key,
                    assessment_group_code=key.split(' ', 1)[0],
                    module_cats=value[0][0]
                )

                for assessment in value:
                    Assessment.objects.create(
                        assessment_group=assessment_group,
                        assessment_name=assessment[1],
                        percentage=float(assessment[2].strip('%'))
                    )

crawlable_links = [
    ['19/20', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/'],
    ['18/19', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/'],
    ['17/18', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201718/undergraduate-1718/undergraduate-copy/'],
    ['16/17', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201617/undergraduate-1617/ug_archive_201617/'],
    ['15/16', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate-1516']
]

def start():
    print('*** Starting Module Scrape ***')
    # for link in crawlable_links:
    #     get_faculties(link)
    get_faculties(crawlable_links[2])
    print('*** Finished Module Scrape ***')