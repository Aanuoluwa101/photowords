import json
import boto3
import uuid
from datetime import datetime
import pytz
import os
from utils import validate_images, add_group_to_all_groups


DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['GROUPS_DYNAMODB_TABLE'])
s3_client = boto3.client('s3')

    
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        hint = body.get('hint')
        images = body.get('images')

        claims = event['requestContext']['authorizer']['claims']
        username = claims.get('cognito:username') 

        validate_images(images)
        group_id = str(uuid.uuid4())
        created_at = datetime.now(pytz.UTC).isoformat()

        item = {
            'id': group_id,
            'answer': answer,
            'difficulty': difficulty,
            'hint': hint,
            'images': [
                {
                    'tag': image['tag'],
                    'start_index': image['start_index'],
                    'end_index': image['end_index'],
                    'position': image['position']
                } for image in images
            ],
            'created_at': created_at,
            'created_by': username
        }

        table.put_item(Item=item)
        add_group_to_all_groups(group_id)

        # save to storage 
        data = body.copy() 
        data['id'] = group_id
        data['created_at'] = created_at
        object_key = f'groups/{group_id}'
        s3_client.put_object(
            Bucket=S3_BUCKET, 
            Key=object_key, 
            Body=json.dumps(data),
            ContentType="application/json"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Group saved successfully!',
                'data': {
                    'id': group_id,
                    'answer': answer,
                    'difficulty': difficulty,
                    'hint': hint,
                    'images': images
                }
            })
        }

    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
    


# utils.py
import boto3
import os

dynamodb = boto3.resource('dynamodb')
images_table = dynamodb.Table(os.environ['IMAGES_DYNAMODB_TABLE'])
groups_table = dynamodb.Table(os.environ['GROUPS_DYNAMODB_TABLE'])
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
            raise ValueError(f"Invalid start_index or end_index for tag '{tag}'.")

        if start_index >= end_index:
            raise ValueError(f"start_index must be less than end_index for tag '{tag}'.")

        if not check_image_exists_in_db(tag):
            raise ValueError(f"'{tag}' does not exist in db")
        
        if not check_image_exists_in_s3(tag):
            raise ValueError(f"'{tag}' does not exist in s3")
        
def add_group_to_all_groups(group_id):
    try:
        groups_table.update_item(
            Key={'id': 'all_groups'},
            UpdateExpression="SET #groups = list_append(#groups, :new_group_id)",
            ExpressionAttributeNames={
                '#groups': 'groups'
            },
            ExpressionAttributeValues={
                ':new_group_id': [group_id]
            }
        )
    except Exception as e:
        raise Exception(f"Error updating 'all_groups': {str(e)}")