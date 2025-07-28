"""
This function registers a newly uploaded image by processing S3 
event records. For each image, it checks if the image 
is in the correct S3 folder, ensures the tag is unique in DynamoDB, 
saves the image details to DynamoDB, and adds the tag to a Redis cache.
 It returns a success or error message in JSON format.
"""


import json
import boto3
import redis
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from redis_client import ElastiCacheIAMProvider


S3_BUCKET = os.environ['S3_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_CACHE_NAME = os.environ.get("REDIS_CACHE_NAME")


# Initialize resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

s3 = boto3.resource('s3')

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


def lambda_handler(event, context):
    try:
        for record in event['Records']:
            s3_bucket = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']

            if not object_key.startswith("images/"):
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'Image key "{object_key}" not in images folder.'
                    })
                }

            tag = object_key.split("/")[-1].split(".")[0]

            # check if image exists in DB
            response = table.get_item(Key={'tag': tag})
            if 'Item' in response:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'An image with the tag "{tag}" is already registered.'
                    })
                }

            # Save image details in DynamoDB
            table.put_item(Item={
                'tag': tag,
                'uploaded_at': datetime.now(tz=ZoneInfo("UTC")).isoformat()
            })

            # Add to Redis SET
            redis_client.sadd('all_images', tag)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing complete.'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
