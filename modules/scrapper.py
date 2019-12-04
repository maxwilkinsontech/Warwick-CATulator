"""
In order to get the data on each module, I have scrapped Warwick's Module
catalog (https://warwick.ac.uk/services/aro/dar/quality/modules/).
"""
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

from .models import Module, AssessmentGroup, Assessment

def get_faculties(request_data):
    """Get all the factulties for the undergraduate."""
    response = requests.get(request_data[2])
    soup = BeautifulSoup(response.text, 'html.parser')

    for ultag in soup.findAll('ul', class_='list-unstyled'):
        for litag in ultag.findAll('li'):
            faculty_modules_link = litag.find('a').get('href', None)
            if faculty_modules_link is None:
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
                continue
            try:
                get_module_info(request_data, link, module_link)
            except AttributeError:
                continue

def get_module_info(request_data, link, module_link):
    url = request_data[2] + link + '/' + module_link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    module_info = soup.find('ul', class_='list-unstyled').findAll('li')

    # Get the Module info and create it 
    module_code = module_info[0].text.split(': ')[1]
    module_name = module_info[1].text.split(': ')[1]
    module_faculty = module_info[2].text.split(': ')[1]

    if not Module.objects.filter(module_code=module_code).exists():

        module = Module.objects.create(
            level=request_data[1],
            academic_year=request_data[0],
            faculty=module_faculty,
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

crawlable_links = [
    ['19/20', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/'],
    ['18/19', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819'],
    ['17/18', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201718/undergraduate-1718/undergraduate-copy'],
    ['16/17', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/archive201617/undergraduate-1617/ug_archive_201617'],
    ['15/16', 'Undergraduate', 'https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate-1516']
]

def start():
    print('*** Starting Module Scrape ***')
    # for link in crawlable_links:
    #     get_faculties(link)
    get_faculties(crawlable_links[0])
    print('*** Finished Module Scrape ***')