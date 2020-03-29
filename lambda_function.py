import base64
import json
import os
import uuid
from urllib.parse import unquote_plus

import boto3
import requests

FD_API_KEY = os.environ.get('FD_FD_API_KEY')
FD_DOMAIN = os.environ.get('FD_FD_DOMAIN')
FD_PASSWORD = os.environ.get('FD_FD_PASSWORD')
s3_client = boto3.client('s3')

CLICKUP_ACCESS_TOKEN = os.environ['CLICKUP_ACCESS_TOKEN']
CLICKUP_LIST_ID = os.environ['CLICKUP_LIST_ID']


def create_content(evidence, freshdesk_url):
    fyle_user = json.loads(evidence['local_storage'].get('fyle.user', ''))
    content = 'description: \n'
    content += '\n url: ' + evidence['url']
    if fyle_user:
        content += '\n email: ' + fyle_user['us']['email']
        content += '\n org_name: ' + fyle_user['ou']['org_name']
        content += '\n org_id: ' + fyle_user['ou']['org_id']
        content += '\n org_user_id: ' + fyle_user['ou']['id']
    content += '\n freshdesk_url: ' + freshdesk_url
    return content


def create_clickup_task(evidence, freshdesk_url=None, screenshot_file_name=None, evidence_file_name=None):
    clickup_task = {'name': evidence['title'],
                    'content': create_content(evidence, freshdesk_url),
                    'status': 'Open',
                    'priority': 3
                    }

    headers = {
        'Authorization': CLICKUP_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }

    resp = requests.post(f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task', data=json.dumps(clickup_task),
                         headers=headers)
    print('reached 1')
    if resp.status_code == 200:
        created_task = resp.json()
        task_id = created_task['id']
        files = [
            ('attachment', open(screenshot_file_name, 'rb'))
        ]
        headers = {
            'Authorization': CLICKUP_ACCESS_TOKEN

        }
        resp1 = requests.post(f'https://api.clickup.com/api/v2/task/{task_id}/attachment', data={}, files=files,
                              headers=headers)
        print(resp1.status_code)

        files = [
            ('attachment', open(evidence_file_name, 'rb'))
        ]
        resp2 = requests.post(f'https://api.clickup.com/api/v2/task/{task_id}/attachment', data={}, files=files,
                              headers=headers)

        print(resp2.status_code)


def image_to_b64(path):
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read())


def save_screenshot(b64_image, path):
    with open(path, 'wb') as fh:
        fh.write(base64.decodebytes(b64_image))


def save_evidence(evidence, path):
    with open(path, 'w') as write_file:
        json.dump(evidence, write_file, indent=2)


def create_description(description_input):
    NA = 'NA'

    description = '''
    url -> {}
    email -> {}
    org_name -> {}
    org_id -> {}
    org_user_id -> {}
    '''.format(
        description_input.get('url', NA),
        description_input.get('email', NA),
        description_input.get('org_name', NA),
        description_input.get('org_id', NA),
        description_input.get('org_user_id', NA))

    return description


def create_fd_ticket(evidence, screenshot_file_name, evidence_file_name):
    description = {'url': evidence['url']}

    fyle_user = evidence['local_storage'].get('fyle.user')
    fyle_user_json = json.loads(fyle_user) if fyle_user else None
    if fyle_user_json:
        description['email'] = fyle_user_json['us']['email']
        description['org_name'] = fyle_user_json['ou']['org_name']
        description['org_id'] = fyle_user_json['ou']['org_id']
        description['org_user_id'] = fyle_user_json['ou']['id']

    multipart_data = [
        ('email', (None, 'bp@fyle.in')),
        ('subject', (None, evidence['title'])),
        ('status', (None, '2')),
        ('priority', (None, '2')),
        ('attachments[]', (screenshot_file_name, open(screenshot_file_name, 'rb'), 'image/png')),
        ('attachments[]', (evidence_file_name, open(evidence_file_name, 'rb'), 'application/json')),
        ('description', (None, '<pre>' + create_description(description) + '</pre>'))
    ]

    r = requests.post('https://' + FD_DOMAIN + '.freshdesk.com/api/v2/tickets', auth=(FD_API_KEY, FD_PASSWORD),
                      files=multipart_data)

    if r.status_code == 201:
        id = str(r.json().get('id'))
        print('Ticket created successfully, the response is given below' + id)
        print('Location Header : ' + r.headers['Location'])
        return 'https://' + FD_DOMAIN + '.freshdesk.com/a/tickets/' + id
    else:
        print('Failed to create ticket, errors are displayed below,')
        response = json.loads(r.content)
        print(response['errors'])

        print('x-request-id : ' + r.headers['x-request-id'])
        print('Status Code : ' + str(r.status_code))


def study_evidence(evidence, create_ticket=False):
    screenshot_file_name = 'screenshot.png'
    save_screenshot(evidence['screenshot_encoded'][22:].encode(), '/tmp/' + screenshot_file_name)

    evidence_file_name = 'evidence.json'
    save_evidence(evidence, '/tmp/' + evidence_file_name)

    if create_ticket:
        fd_url = create_fd_ticket(evidence, '/tmp/' + screenshot_file_name, '/tmp/' + evidence_file_name)
        print(fd_url)
        create_clickup_task(evidence, fd_url, '/tmp/' + screenshot_file_name,
                            '/tmp/' + evidence_file_name)


def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        s3_client.download_file(bucket, key, download_path)
        with open(download_path, encoding='utf-8') as file:
            evidence = json.load(file)

    study_evidence(evidence, True)
    return {
        'statusCode': 200,
    }
