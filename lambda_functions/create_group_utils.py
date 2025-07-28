# utils.py
import boto3
import os
import redis
import json


# dynamodb
dynamodb = boto3.resource('dynamodb')
images_table = dynamodb.Table(os.environ['IMAGES_DYNAMODB_TABLE'])
groups_table = dynamodb.Table(os.environ['GROUPS_DYNAMODB_TABLE'])

# s3
S3_BUCKET = os.environ['S3_BUCKET']
s3_client = boto3.client('s3')


def check_image_exists_in_db(tag):
    response = images_table.get_item(
        Key={"tag": tag}
    )
    return "Item" in response


def check_image_exists_in_s3(tag):
    object_key = f"images/{tag}"
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=object_key)
        return True 
    except s3_client.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != '403' and error_code != '404':
            raise e
        return False

def validate_images(images):
    for image in images:
        tag = image.get('tag')
        start_index = image.get('start_index')
        end_index = image.get('end_index')

        if start_index < 0 or end_index > len(tag):
            raise ValueError(f"Invalid start_index or end_index.")

        if start_index >= end_index:
            raise ValueError(f"start_index must be less than end_index.")

        if not check_image_exists_in_db(tag):
            raise ValueError(f"'{tag}' does not exist in db")
        
        if not check_image_exists_in_s3(tag):
            raise ValueError(f"'{tag}' does not exist in s3")
