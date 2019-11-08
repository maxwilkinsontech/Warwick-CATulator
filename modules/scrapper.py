"""
In order to get the data on each module, I have scrapped Warwick's Module
catalog (https://warwick.ac.uk/services/aro/dar/quality/modules/).
"""
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

# from modules.models import Module, AssessmentGroup, Assessment

def get_faculties(request_data):
    """Get all the factulties for the undergraduate."""
    response = requests.get(request_data[2])
    soup = BeautifulSoup(response.text, 'html.parser')

    for ultag in soup.findAll('ul', class_='list-unstyled'):
        for litag in ultag.findAll('li'):
            faculty_modules_link = litag.find('a')['href']
            get_faculty_modules(request_data, faculty_modules_link)
            break
        break

def get_faculty_modules(request_data, link):
    url = request_data[2] + link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for ultag in soup.findAll('ul', class_='list-unstyled'):
        for litag in ultag.findAll('li'):
            module_link = litag.find('a')['href']
            get_module_info(request_data, link, module_link)
            break
        break
            
def get_module_info(request_data, link, module_link):
    url = request_data[2] + link + '/' + module_link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    module_info = soup.find('ul', class_='list-unstyled').findAll('li')

    # Get the Module info and create it 
    module_code = module_info[0].text.split(': ')[1]
    module_name = module_info[1].text.split(': ')[1]
    module_faculty = module_info[2].text.split(': ')[1]
    module_cats = module_info[3].text.split(': ')[1]

    module = Module.objects.create(
        level=request_data[1],
        academic_year=request_data[0],
        faculty=module_faculty,
        module_code=module_code,
        module_name=module_name,
        cats=module_cats
    )

    # Get the assessment infomation for the module
    assessment_groups = soup.find('table', class_='table table-striped').find('tbody').findAll('tr')
    # create a dictionary, key is the name of the AssessmentGroup and value
    # is a list of Assessments
    assessment_groups_dict = {}
    prev_assessment_name = None
    for row in assessment_groups[1:]:
        cols = row.findAll('td')
        assessment_name = cols[0].text.strip()

        if len(assessment_name) > 1:
            assessment_groups_dict[assessment_name] = [[cols[1].text, cols[2].text]]
        else:
            a = assessment_groups_dict[prev_assessment].append([cols[1].text, cols[2].text])

        prev_assessment_name = assessment_name
    
    for key, value in assessment_groups_dict.items():
        assessment_group = AssessmentGroup.objects.create(
            module=module,
            assessment_group_name=key
        )

        for assessment in value:
            Assessment.objects.create(
                assessment_group=assessment_group,
                assessment_name=assessment[0],
                percentage=decimal(assessment[1])
            )

crawlable_links = [
    ['19/20', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/'],
    ['18/19', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819'],
    ['17/18', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201718/undergraduate-1718/undergraduate-copy'],
    ['16/17', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201617/undergraduate-1617/ug_archive_201617'],
    ['15/16', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate-1516']
]

get_faculties(crawlable_links[0])
