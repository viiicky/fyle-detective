import logging
import boto3
from botocore.exceptions import ClientError
import json
import os

ACCESS_KEY = os.environ['FD_AWS_ACCESS_KEY']
SECRET_KEY = os.environ['FD_AWS_SECRET_KEY']

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
    	aws_access_key_id=ACCESS_KEY,
    	aws_secret_access_key=SECRET_KEY
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
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY
                    )
    content_object = s3.Object(bucket, file_name)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    return json_content


# print(upload_file('bp_vikas2.json', 'fyle-hackathon'))
print(read_file('bp_vikas2.json', 'fyle-hackathon'))

# Credits:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
# https://stackoverflow.com/questions/40995251/reading-an-json-file-from-s3-using-python-boto3