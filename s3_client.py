import logging
import boto3
import requests
import config

from botocore.exceptions import ClientError

class S3Client:

    global s3
    session = boto3.Session(aws_access_key_id=config.aws_access_key_id,
                            aws_secret_access_key=config.aws_secret_access_key)
    s3 = boto3.resource('s3')

    def create_bucket(bucket_name, region=None):
        try:
            if region is None:
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client = boto3.client('s3', region_name=region)
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=bucket_name,
                                        CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def get_buckets():
        buckets = []
        for bucket in s3.buckets.all():
            buckets.append(bucket.name)
        return buckets

    def delete_bucket(bucket_name):
        bucket = s3.Bucket(bucket_name)
        try:
            bucket.delete()
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_file(file_name, bucket, object_name=None):
        if object_name is None:
            object_name = file_name

        try:
            s3.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_file_obj(self, file_name, bucket, object_name=None):
        if object_name is None:
            object_name = file_name

        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                s3.upload_fileobj(file, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True
    
    def upload_file_obj_from_web(self, web_url, folder=None, object_name=None):
        
        if object_name is None:
            object_name = web_url.split('/')[-1]
        if folder:
            object_name = folder + '/' + object_name

        for bucket in s3.buckets.all():
            if bucket.name == config.bucket_name:
                request = requests.get(web_url, stream=True)
                req_data = request.raw.read()
                try:
                    s3.Bucket(config.bucket_name).put_object(Key=object_name, Body=req_data)
                    print('File uploaded successfully')
                except ClientError as e:
                    logging.error(e)
                    return False

    def download_file(file_name, bucket, object_name=None):
        if object_name is None:
            object_name = file_name

        try:
            s3.download_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def download_file_obj(file_name, bucket, object_name=None):
        if object_name is None:
            object_name = file_name

        try:
            with open(file_name, 'wb') as file:
                s3.download_fileobj(bucket, object_name, file)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_file(bucket, object_name):
        try:
            s3.delete_object(Bucket=bucket, Key=object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True