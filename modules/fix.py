import requests
from bs4 import BeautifulSoup

from .models import Module, AssessmentGroup, Assessment
from users.models import User

def get_all_modules():
    modules = Module.objects.values_list('module_code', flat=True).distinct()
    print('Distinct Modules: ' + str(modules.count()))

    modules_19 = list(Module.objects.filter(academic_year='19/20').values_list('module_code', flat=True).distinct())
    modules_18 = list(Module.objects.filter(academic_year='18/19').values_list('module_code', flat=True).distinct())
    modules_17 = list(Module.objects.filter(academic_year='17/18').values_list('module_code', flat=True).distinct())

    print('19/20 Modules: ' + str(len(modules_19)))
    print('18/19 Modules: ' + str(len(modules_18)))
    print('17/18 Modules: ' + str(len(modules_17)))

    missing_modules_19 = [x for x in set(modules_17 + modules_18) if x not in modules_19]
    missing_modules_18 = [x for x in set(modules_17 + modules_19) if x not in modules_18]
    missing_modules_17 = [x for x in set(modules_18 + modules_19) if x not in modules_17]

    print('19/20 Missing Modules: ' + str(len(missing_modules_19)))
    print('18/19 Missing Modules: ' + str(len(missing_modules_18)))
    print('17/18 Missing Modules: ' + str(len(missing_modules_17)))

    print(missing_modules_19)
    print(missing_modules_18)

    URLS = [
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/im/qs301', '19/20'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/po/qs104', '19/20'],
        # ['https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/po/qs103', '19/20'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/ln/ll2b6', '19/20'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/undergraduate/im/qs304', '19/20'],

        ['https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/po/qs203', '18/19'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/po/QS105', '18/19'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/po/QS202', '18/19'],
        # ['https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/po/QS103', '18/19'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/im/qs304', '18/19'],
        ['https://warwick.ac.uk/services/aro/dar/quality/modules/archive201819/undergraduate-1819/po/QS305', '18/19'],
    ]

    for url in URLS:
        print(url)
        response = requests.get(url[0])
        soup = BeautifulSoup(response.text, 'html.parser')
        module_info = soup.find('ul', class_='list-unstyled').findAll('li')

        # Get the Module info and create it 
        module_code = module_info[0].text.split(': ')[1]
        module_name = module_info[1].text.split(': ')[1]
        module_faculty = module_info[2].text.split(': ')[1]

        if not Module.objects.filter(module_code=module_code, academic_year=url[1]).exists():

            module = Module.objects.create(
                academic_year=url[1],
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