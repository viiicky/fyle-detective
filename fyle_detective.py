import logging
import boto3
from botocore.exceptions import ClientError
import json
import os
import requests


AWS_ACCESS_KEY = os.environ['FD_AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['FD_AWS_SECRET_KEY']

FD_API_KEY = os.environ['FD_FD_API_KEY']
FD_DOMAIN = os.environ['FD_FD_DOMAIN']
FD_PASSWORD = os.environ['FD_FD_PASSWORD']

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client(
	    's3',
    	aws_access_key_id=AWS_ACCESS_KEY,
    	aws_secret_access_key=AWS_SECRET_KEY
	)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def read_file(file_name, bucket):
    """Read a file from an S3 bucket

    :param file_name: File to read
    :param bucket: Bucket to read from
    :return: the file content
    """
    s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY
                    )
    content_object = s3.Object(bucket, file_name)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    return json_content


def create_fd_ticket():
    multipart_data = [
        ('email', (None,'bp@fyle.in')),
        ('subject', (None, 'FD: hastalavista')),
        ('status', (None, '2')),
        ('priority', (None, '2')),
        ('attachments[]', ('sample.png', open('sample.png', 'rb'), 'image/png')),
        ('description', (None, 'FD: Back in Black'))
    ]

    r = requests.post("https://"+ FD_DOMAIN +".freshdesk.com/api/v2/tickets", auth = (FD_API_KEY, FD_PASSWORD), files = multipart_data)

    if r.status_code == 201:
      print("Ticket created successfully, the response is given below" + r.text)
      print("Location Header : " + r.headers['Location'])
    else:
      print("Failed to create ticket, errors are displayed below,")
      response = json.loads(r.content)
      print(response["errors"])

      print("x-request-id : " + r.headers['x-request-id'])
      print("Status Code : " + str(r.status_code))

# print(upload_file('sample.png', 'fyle-hackathon'))
# print(read_file('bp_vikas2.json', 'fyle-hackathon'))
print(create_fd_ticket())

# Credits:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
# https://stackoverflow.com/questions/40995251/reading-an-json-file-from-s3-using-python-boto3
#
# https://developers.freshdesk.com/api/#tickets
# https://github.com/freshdesk/fresh-samples/blob/master/Python/create_ticket_attachment.py
# https://github.com/freshdesk/fresh-samples/issues/44
# https://stackoverflow.com/questions/31708519/request-returns-bytes-and-im-failing-to-decode-them