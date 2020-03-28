## Quick python utility to upload files and read files to/from Amazon S3

* Make sure you get the dependencies installed from `requirements.txt`
* Make sure you have the aws access and secret keys set into the following envs respectively for this script to work: `FD_AWS_ACCESS_KEY`, `FD_AWS_SECRET_KEY`
* `upload_file(file_name, bucket, object_name=None)` takes the path to file, and bucket name as the params. Object name is an optional param. If left empty, the same name as file is used for object. This method uploads the file to S3.
* `read_file(file_name, bucket)` takes the path to file and bucket name as the params. This method reads the file from S3.
