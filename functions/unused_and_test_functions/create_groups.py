import json
import boto3
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import redis
from utils import validate_images
from redis_client import ElastiCacheIAMProvider


DYNAMODB_TABLE = os.environ['GROUPS_DYNAMODB_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['GROUPS_DYNAMODB_TABLE'])
s3_client = boto3.client('s3')


# Redis
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")

creds_provider = ElastiCacheIAMProvider(
    user=REDIS_USERNAME,
    cache_name=REDIS_CACHE_NAME,
    is_serverless=False
)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    credential_provider=creds_provider,
    ssl=True,
    ssl_cert_reqs="none",
    decode_responses=True
)



def cache_group_in_redis(group_data):
    try:
        group_id = group_data["id"]
        redis_client.set(f"group:{group_id}", json.dumps(group_data))     
        redis_client.sadd("all_groups", group_id)
    except Exception as e:
        raise Exception(f"Error caching group in Redis: {str(e)}")


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        hint = body.get('hint')
        images = body.get('images')

        username = event['requestContext']['authorizer']['claims']["cognito:username"]
        validate_images(images)
        group_id = str(uuid.uuid4())
        created_at = datetime.now(tz=ZoneInfo("UTC")).isoformat()

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
        cache_group_in_redis(item)

        # # save to storage......why
        # data = body.copy() 
        # data['id'] = group_id
        # data['created_at'] = created_at
        # object_key = f'groups/{group_id}'
        # s3_client.put_object(
        #     Bucket=S3_BUCKET, 
        #     Key=object_key, 
        #     Body=json.dumps(data),
        #     ContentType="application/json"
        # )
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Group saved successfully!',
                'data': {
                    'id': group_id
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