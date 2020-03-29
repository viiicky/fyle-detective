import json
import os

import requests

# from fyle_detective import study_evidence

CLICKUP_ACCESS_TOKEN = os.environ['CLICKUP_API_KEY']
CLICKUP_LIST_ID = os.environ['CLICKUP_LIST_ID']


def create_content(evidence):
    fyle_user = json.loads(evidence['local_storage'].get('fyle.user', ''))
    content = 'description:'
    content += '\n url: ' + evidence['url']
    if fyle_user:
        content += '\n email: ' + fyle_user['us']['email']
        content += '\n org_name: ' + fyle_user['ou']['org_name']
        content += '\n org_id: ' + fyle_user['ou']['org_id']
        content += '\n org_user_id: ' + fyle_user['ou']['id']
    return content


def create_clickup_task(evidence, screenshot_file_name=None, evidence_file_name=None):
    # clickup_task = {'name': evidence['title'],
    #                 'content': create_content(evidence),
    #                 'status': 'Open',
    #                 'priority': 3
    #                 }
    #
    # headers = {
    #     'Authorization': CLICKUP_ACCESS_TOKEN,
    #     'Content-Type': 'application/json'
    # }
    #
    # resp = requests.post(f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task', data=json.dumps(clickup_task),
    #                      headers=headers)
    # print(resp.json())
    # if resp.status_code == 200:
    #     created_task = resp.json()
    task_id = '2hjwdj'
    print(task_id)
    files = [
        ('attachment', open('screenshot.png', 'rb'))
    ]
    headers = {
        'Authorization': CLICKUP_ACCESS_TOKEN

    }

    request = requests.post(f'https://api.clickup.com/api/v2/task/{task_id}/attachment', data={}, files=files,
                            headers=headers)
    print(request.status_code)
    print(request.json())


with open('evidence.json', encoding='utf-8') as file:
    evidence = json.load(file)
    create_clickup_task(evidence)
    # study_evidence(evidence, True)
